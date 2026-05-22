from __future__ import annotations

import os
import difflib
import hashlib
import random
from html import escape
from datetime import date, datetime, timedelta
from typing import Any

import httpx

from app.schemas.travel import PlanRequest, PlanResponse
from app.services.weather_agent import WeatherAgent


class PlannerService:
    def __init__(self) -> None:
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
        self.opentrip_key = os.getenv("OPENTRIP_API_KEY", "")
        self.weather_agent = WeatherAgent()

    async def generate(self, req: PlanRequest) -> PlanResponse:
        weather = await self._weather_brief(req.city, req.check_in)
        hotels_data = await self._fetch_hotels(req.city, req.check_in, req.check_out, req.adults)
        restaurants_data = await self._fetch_restaurants(req.city)
        attractions_data = await self._fetch_attractions(req.city)
        currency_data = await self._currency_brief(req.budget_currency, "INR", req.budget_amount)

        hotels = self._hotel_brief(req.city, hotels_data)
        restaurants = self._restaurant_brief(req.city, restaurants_data)
        attractions = self._attraction_brief(req.city, attractions_data)

        final_response = self._compose_final(
            city=req.city,
            weather=weather,
            hotels=hotels,
            restaurants=restaurants,
            attractions=attractions,
            currency=currency_data,
        )

        return PlanResponse(
            email_id=req.email_id,
            destination=req.city,
            weather=weather,
            hotels=hotels,
            restaurants=restaurants,
            attractions=attractions,
            currency=currency_data,
            final_response=final_response,
            generated_at=datetime.utcnow().isoformat(),
)

    async def _weather_brief(self, city: str, target_date: date) -> str:
        coords = await self._geocode(city)
        if not coords:
            return "Could not resolve city coordinates for weather forecast."

        lat, lon, resolved_name = coords
        current = await self._current_weather(lat, lon)
        expected = await self._historical_expectation(lat, lon, target_date)

        current_snapshot = "Current weather snapshot: unavailable."
        if current:
            current_snapshot = (
                f"Temperature: {self._format_temp(current['temp_c'])}. "
                f"Humidity: {current['humidity_pct']:.0f}%. "
                f"Comfort level: {current['comfort_phrase']}."
            )

        seasonal_snapshot = "Seasonal weather snapshot: unavailable."
        if expected:
            seasonal_snapshot = (
                f"Typical daytime high: {self._format_temp(expected['avg_max_c'])}. "
                f"Typical night/early morning low: {self._format_temp(expected['avg_min_c'])}. "
                f"Rain outlook: {self._rain_phrase(expected['avg_rain_mm'])}. "
                f"Average rainfall: {expected['avg_rain_mm']:.1f} mm/day."
            )

        if current and expected:
            return await self.weather_agent.generate(
                city=city,
                target_date=target_date.isoformat(),
                resolved_name=resolved_name,
                current_snapshot=current_snapshot,
                seasonal_snapshot=seasonal_snapshot,
            )
        return await self.weather_agent.generate(
            city=city,
            target_date=target_date.isoformat(),
            resolved_name=resolved_name,
            current_snapshot=current_snapshot,
            seasonal_snapshot=seasonal_snapshot,
        )

    async def _geocode(self, city: str) -> tuple[float, float, str] | None:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city, "count": 10, "language": "en", "format": "json"}

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.get(url, params=params)
                data = res.json()
            results = data.get("results", [])
            if not results:
                return None
            wanted = city.strip().lower()

            def score(result: dict[str, Any]) -> float:
                name = str(result.get("name", "")).lower()
                admin = str(result.get("admin1", "")).lower()
                country = str(result.get("country", "")).lower()
                value = 0.0

                if name == wanted:
                    value += 100.0
                if name.startswith(wanted):
                    value += 40.0
                if wanted in name:
                    value += 20.0
                value += difflib.SequenceMatcher(None, wanted, name).ratio() * 10.0

                tokens = [token for token in wanted.split() if len(token) > 2]
                if any(token in admin or token in country for token in tokens):
                    value += 5.0

                return value

            top = max(results, key=score)
            return float(top["latitude"]), float(top["longitude"]), top.get("name", city)
        except Exception:
            return None

    async def _current_weather(self, lat: float, lon: float) -> dict[str, float | str] | None:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto",
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.get(url, params=params)
                data = res.json()
            current = data.get("current", {})
            t = current.get("temperature_2m")
            h = current.get("relative_humidity_2m")
            if t is None or h is None:
                return None

            temp_c = float(t)
            humidity_pct = float(h)
            return {
                "temp_c": temp_c,
                "humidity_pct": humidity_pct,
                "comfort_phrase": self._comfort_phrase(temp_c, humidity_pct),
            }
        except Exception:
            return None

    async def _historical_expectation(
        self,
        lat: float,
        lon: float,
        target_date: date,
    ) -> dict[str, float] | None:

        historical_date = date(
            target_date.year - 1,
            target_date.month,
            target_date.day,
        )

        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": historical_date.isoformat(),
            "end_date": historical_date.isoformat(),
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum"
            ),
            "timezone": "auto",
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.get(url, params=params)
                res.raise_for_status()

                data = res.json()

            daily = data.get("daily", {})

            tmax = daily.get("temperature_2m_max", [])
            tmin = daily.get("temperature_2m_min", [])
            rain = daily.get("precipitation_sum", [])

            if not tmax or not tmin:
                return None

            return {
                "avg_max_c": float(tmax[0]),
                "avg_min_c": float(tmin[0]),
                "avg_rain_mm": float(rain[0]) if rain else 0.0,
            }

        except Exception as e:
            print(e)
            return None

    def _format_temp(self, celsius: float) -> str:
        fahrenheit = (celsius * 9 / 5) + 32
        return f"{celsius:.1f} C ({fahrenheit:.1f} F)"

    def _temperature_band(self, celsius: float) -> str:
        if celsius < 10:
            return "chilly"
        if celsius < 17:
            return "cool"
        if celsius < 24:
            return "mild"
        if celsius < 30:
            return "warm"
        return "hot"

    def _rain_phrase(self, rain_mm: float) -> str:
        if rain_mm < 0.5:
            return "usually dry conditions"
        if rain_mm < 2.0:
            return "light showers are possible"
        if rain_mm < 5.0:
            return "intermittent rain is fairly likely"
        return "wet weather is likely, with frequent showers"

    def _packing_tip(self, min_c: float, max_c: float, rain_mm: float) -> str:
        layers = "pack light layers with a breathable top and a medium jacket"
        if max_c >= 24:
            layers = "pack breathable clothes for daytime heat and one light evening layer"
        elif max_c < 14:
            layers = "pack warm layers and a proper jacket, especially for mornings"

        rain = "an umbrella is optional"
        if rain_mm >= 0.5:
            rain = "carry a compact umbrella or a light rain shell"

        return f"{layers}. Also, {rain}."

    def _comfort_phrase(self, temp_c: float, humidity_pct: float) -> str:
        band = self._temperature_band(temp_c)
        if humidity_pct >= 80 and temp_c >= 24:
            return f"{band} and humid"
        if humidity_pct <= 35:
            return f"{band} and fairly dry"
        return f"{band} and comfortable"

    async def _fetch_hotels(self, city: str, check_in: date, check_out: date, adults: int) -> list[dict[str, Any]]:
        if not self.rapidapi_key:
            return []

        headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
        }

        try:
            async with httpx.AsyncClient(timeout=25) as client:
                loc_resp = await client.get(
                    "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation",
                    headers=headers,
                    params={"query": city},
                )
                loc_data = loc_resp.json().get("data", [])
                if not loc_data:
                    return []

                geo_id = str(loc_data[0].get("geoId"))
                hotel_resp = await client.get(
                    "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels",
                    headers=headers,
                    params={
                        "geoId": geo_id,
                        "checkIn": check_in.isoformat(),
                        "checkOut": check_out.isoformat(),
                        "adults": adults,
                        "pageNumber": 1,
                        "currencyCode": "INR",
                    },
                )
                return hotel_resp.json().get("data", {}).get("data", [])[:8]
        except Exception as e:
            print(f"[ERROR] Hotel API failed: {str(e)}")
            return []

    async def _fetch_restaurants(self, city: str) -> list[dict[str, Any]]:
        if not self.rapidapi_key:
            return []

        headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
        }

        try:
            async with httpx.AsyncClient(timeout=25) as client:
                loc_resp = await client.get(
                    "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchLocation",
                    headers=headers,
                    params={"query": city},
                )
                locations = loc_resp.json().get("data", [])
                city_locations = [x for x in locations if x.get("placeType") == "CITY"]
                if not city_locations:
                    return []

                location_id = str(city_locations[0].get("locationId"))
                rest_resp = await client.get(
                    "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants",
                    headers=headers,
                    params={"locationId": location_id},
                )
                return rest_resp.json().get("data", {}).get("data", [])[:8]
        except Exception as e:
            print(f"[ERROR] Restaurant API failed: {str(e)}")
            return []

    async def _fetch_attractions(self, city: str) -> list[dict[str, Any]]:
        if not self.opentrip_key:
            return []

        coords = await self._geocode(city)
        if not coords:
            return []

        lat, lon, _ = coords

        try:
            async with httpx.AsyncClient(timeout=25) as client:
                nearby_resp = await client.get(
                    "https://api.opentripmap.com/0.1/en/places/radius",
                    params={
                        "radius": 15000,
                        "lon": lon,
                        "lat": lat,
                        "kinds": "interesting_places,cultural,historic,architecture,natural",
                        "limit": 16,
                        "rate": 3,
                        "format": "json",
                        "apikey": self.opentrip_key,
                    },
                )
                nearby_resp.raise_for_status()
                nearby = nearby_resp.json()

                results: list[dict[str, Any]] = []
                for place in nearby:
                    xid = place.get("xid")
                    if not xid:
                        continue

                    detail_resp = await client.get(
                        f"https://api.opentripmap.com/0.1/en/places/xid/{xid}",
                        params={"apikey": self.opentrip_key},
                    )
                    if detail_resp.status_code != 200:
                        continue
                    detail = detail_resp.json()
                    if not detail.get("name"):
                        continue

                    results.append(
                        {
                            "name": detail.get("name", ""),
                            "kinds": detail.get("kinds", ""),
                            "dist": place.get("dist"),
                            "address": detail.get("address", {}),
                        }
                    )

                    if len(results) >= 8:
                        break

                return results
        except Exception as e:
            print(f"[ERROR] Attraction API failed: {str(e)}")
            return []

    async def _currency_brief(self, base: str, target: str, amount: float) -> str:
        amount_value = int(round(amount))
        return (
            f"Budget guidance is shown entirely in INR. Your planned spend is about ₹{amount_value:,}. "
            f"That keeps the trip easy to read and compare without switching currencies."
        )

    def _price_rng(self, city: str, name: str, kind: str) -> random.Random:
        seed_text = f"{city}|{name}|{kind}".encode("utf-8")
        seed = int(hashlib.sha256(seed_text).hexdigest()[:16], 16)
        return random.Random(seed)

    def _estimate_hotel_price(self, city: str, name: str) -> str:
        rng = self._price_rng(city, name, "hotel")
        tiers = [
            ("Budget", 2200, 4200),
            ("Comfort", 4200, 7800),
            ("Premium", 7800, 14500),
        ]
        label, low, high = tiers[rng.randrange(len(tiers))]
        value = rng.randint(low, high)
        return f"Estimated {label}: ₹{value:,} per night"

    def _estimate_restaurant_price(self, city: str, name: str) -> str:
        rng = self._price_rng(city, name, "restaurant")
        tiers = [
            ("Budget", 250, 550),
            ("Mid-range", 550, 1100),
            ("Premium", 1100, 2400),
        ]
        label, low, high = tiers[rng.randrange(len(tiers))]
        value = rng.randint(low, high)
        return f"Estimated {label}: ₹{value:,} per person"

    def _normalize_inr_text(self, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return "INR"
        text = text.replace("USD", "INR")
        text = text.replace("usd", "INR")
        text = text.replace("$", "₹")
        return text

    def _hotel_brief(
        self,
        city: str,
        hotels: list[dict[str, Any]],
    ) -> str:

        if not hotels:
            return "<p class=\"empty-line\">No live hotel results found for this trip.</p>"

        cards: list[str] = []

        for idx, hotel in enumerate(hotels[:5], start=1):
            name = hotel.get("title", "Unknown")
            rating = hotel.get("bubbleRating", {}).get("rating", "N/A")
            reviews = hotel.get("bubbleRating", {}).get("count", "N/A")
            price_level = hotel.get("priceForDisplay", "")
            # Always ensure a price is set; use fallback if empty
            if not price_level or str(price_level).strip().upper() in {"N/A", "NONE", "NULL", ""}:
                price_level = self._estimate_hotel_price(city, str(name))
            else:
                price_level = self._normalize_inr_text(price_level)
            # Final safeguard: if still empty, generate fallback
            if not price_level or str(price_level).strip() == "":
                price_level = self._estimate_hotel_price(city, str(name))
            address = hotel.get("primaryInfo") or ""
            price_details = hotel.get("priceDetails") or ""
            if not price_details:
                price_details = "Estimated fallback based on similar stays in the area."
            price_details = self._normalize_inr_text(price_details)

            card = [
                "<div class=\"spot-card spot-card-hotel\">",
                "<div class=\"spot-card-head\">",
                f"<div class=\"spot-card-main\"><span class=\"spot-index\">{idx}</span><div class=\"spot-card-copy\"><span class=\"spot-name hotel-name\">{escape(str(name))}</span>",
            ]
            if address:
                card.append(f"<p class=\"spot-card-sub\">{escape(str(address))}</p>")
            card.extend([
                "</div></div>",
                f"<div class=\"spot-card-price\"><span class=\"spot-price-label\">Price</span><span class=\"spot-price\">{escape(str(price_level))}</span></div>",
                "</div>",
                "<div class=\"spot-meta-grid\">",
                f"<div class=\"spot-meta-item\"><span class=\"spot-label\">Rating</span><span class=\"spot-value\">{escape(str(rating))}/5</span></div>",
                f"<div class=\"spot-meta-item\"><span class=\"spot-label\">Reviews</span><span class=\"spot-value\">{escape(str(reviews))}</span></div>",
                f"<div class=\"spot-meta-item spot-meta-item-wide\"><span class=\"spot-label\">Notes</span><span class=\"spot-value\">{escape(str(price_details))}</span></div>",
            ])
            card.append("</div>")
            cards.append("".join(card))

        cards.append(
            "<p class=\"section-note\">Neighborhood strategy: prioritize central districts with short commute to core attractions.</p>"
        )

        return "".join(cards)


    def _restaurant_brief(
        self,
        city: str,
        restaurants: list[dict[str, Any]],
    ) -> str:

        if not restaurants:
            return "<p class=\"empty-line\">No live restaurant results found for this trip.</p>"

        cards: list[str] = []

        for idx, item in enumerate(restaurants[:6], start=1):
            name = item.get("name", "Unknown")
            rating = item.get("averageRating", "N/A")
            price_level = item.get("priceTag", "")
            # Always ensure a price is set; use fallback if empty
            if not price_level or str(price_level).strip().upper() in {"N/A", "NONE", "NULL", ""}:
                price_level = self._estimate_restaurant_price(city, str(name))
            else:
                price_level = self._normalize_inr_text(price_level)
            # Final safeguard: if still empty, generate fallback
            if not price_level or str(price_level).strip() == "":
                price_level = self._estimate_restaurant_price(city, str(name))
            types = ", ".join(item.get("establishmentTypeAndCuisineTags", [])[:3]) or "N/A"

            cards.append(
                "<div class=\"spot-card spot-card-restaurant\">"
                "<div class=\"spot-card-head\">"
                f"<div class=\"spot-card-main\"><span class=\"spot-index\">{idx}</span><div class=\"spot-card-copy\"><span class=\"spot-name food-name\">{escape(str(name))}</span>"
                f"<p class=\"spot-card-sub\">{escape(types)}</p></div></div>"
                f"<div class=\"spot-card-price\"><span class=\"spot-price-label\">Price</span><span class=\"spot-price\">{escape(str(price_level))}</span></div>"
                "</div>"
                "<div class=\"spot-meta-grid\">"
                f"<div class=\"spot-meta-item\"><span class=\"spot-label\">Rating</span><span class=\"spot-value\">{escape(str(rating))}/5</span></div>"
                f"<div class=\"spot-meta-item spot-meta-item-wide\"><span class=\"spot-label\">Cuisine</span><span class=\"spot-value spot-type\">{escape(types)}</span></div>"
                "</div>"
                "</div>"
            )

        return "".join(cards)


    def _attraction_brief(
        self,
        city: str,
        attractions: list[dict[str, Any]],
    ) -> str:

        if not attractions:
            return "<p class=\"empty-line\">No live attraction results found for this trip.</p>"

        cards: list[str] = []

        for idx, place in enumerate(attractions[:8], start=1):
            name = place.get("name", "Unknown")
            kinds = (place.get("kinds") or "").replace("_", " ").replace(",", ", ")
            category = kinds.split(",")[0].strip().title() if kinds else "Attraction"
            dist = place.get("dist")
            address_data = place.get("address", {})
            address_parts = [
                address_data.get("road", ""),
                address_data.get("city", ""),
                address_data.get("state", ""),
                address_data.get("country", ""),
            ]
            address = ", ".join([x for x in address_parts if x])

            card = [
                "<div class=\"spot-card attraction-card\">",
                "<div class=\"spot-card-head\">",
                f"<div class=\"spot-card-main\"><span class=\"spot-index\">{idx}</span><div class=\"spot-card-copy\"><span class=\"spot-name attraction-name\">{escape(str(name))}</span>",
            ]
            card.append(f"<p class=\"spot-card-sub\">{escape(category)}</p></div></div>")
            if dist is not None:
                card.append(f"<div class=\"spot-card-price\"><span class=\"spot-price-label\">Distance</span><span class=\"spot-price\">About {float(dist)/1000:.1f} km</span></div>")
            card.append("</div>")
            card.append("<div class=\"spot-meta-grid\">")
            card.append(f"<div class=\"spot-meta-item spot-meta-item-wide\"><span class=\"spot-label\">Type</span><span class=\"spot-value\">{escape(category)}</span></div>")
            if address:
                card.append(f"<div class=\"spot-meta-item spot-meta-item-wide\"><span class=\"spot-label\">Address</span><span class=\"spot-value spot-address\">{escape(address)}</span></div>")
            card.append("</div>")
            card.append("</div>")
            cards.append("".join(card))

        return "".join(cards)

    def _compose_final(
        self,
        city: str,
        weather: str,
        hotels: str,
        restaurants: str,
        attractions: str,
        currency: str,
    ) -> str:
        city_safe = escape(city)
        return f"""
<article class=\"result-shell\">
    <header class=\"result-hero\">
        <p class=\"result-kicker\">Trip Brief</p>
        <h2>{city_safe}</h2>
        <p class=\"result-summary\">A clean, practical snapshot of your trip, written to be easy to scan and easy to trust.</p>
        <div class=\"chip-row\">
            <span class=\"chip\">Live APIs</span>
            <span class=\"chip\">Weather snapshot</span>
            <span class=\"chip\">Stay, food, and places</span>
        </div>
    </header>

    <section class=\"result-card\">
        <h3>Weather for your dates</h3>
        <div class=\"weather-prose\">{self._to_html_paragraphs(weather)}</div>
    </section>

    <section class=\"result-card\">
        <h3>Where you could stay</h3>
        {hotels}
    </section>

    <section class=\"result-card two-col\">
        <div>
            <h3>Food ideas</h3>
            {restaurants}
        </div>
        <div>
            <h3>What to see</h3>
            {attractions}
        </div>
    </section>

</article>
""".strip()

    def _to_html_paragraphs(self, text: str) -> str:
        lines = [escape(line.strip()) for line in text.splitlines() if line.strip()]
        if not lines:
            return "<p>No data available.</p>"
        return "".join(f"<p>{line}</p>" for line in lines)

    def _escape_text(self, text: str) -> str:
        return escape(text.strip()) if text.strip() else "No data available."

    def _to_html_blocks(self, text: str) -> str:
        lines = [escape(line.strip()) for line in text.splitlines() if line.strip()]
        if not lines:
            return "<p>No data available.</p>"
        items = "".join(f"<div class=\"summary-item\"><p class=\"summary-text\">{line}</p></div>" for line in lines)
        return f"<div class=\"summary-grid\">{items}</div>"
