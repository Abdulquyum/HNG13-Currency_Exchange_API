#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class ImageGenerator:
    def __init__(self):
        self.cache_dir = 'cache'
        self.image_path = os.path.join(self.cache_dir, 'summary.png')
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def generate_summary_image(self, countries):
        """
        Generate summary image from countries data
        :param countries: List of country objects
        :return: Boolean indicating success
        """
        try:
            total_countries = len(countries)
            
            # Get top 5 countries by GDP
            top_countries = sorted(
                [c for c in countries if c.estimated_gdp is not None],
                key=lambda x: x.estimated_gdp,
                reverse=True
            )[:5]
            
            # Get last refresh time
            if countries:
                last_refresh = max(country.last_refreshed_at for country in countries if country.last_refreshed_at)
            else:
                last_refresh = datetime.now()

            # Create image
            img_width = 800
            img_height = 600
            image = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Try to use a larger font, fall back to default if not available
            try:
                title_font = ImageFont.truetype("arial.ttf", 32)
                header_font = ImageFont.truetype("arial.ttf", 24)
                text_font = ImageFont.truetype("arial.ttf", 18)
            except IOError:
                # Fallback to default font
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                text_font = ImageFont.load_default()

            # Title
            draw.text((50, 30), "Countries Summary", fill=(0, 0, 0), font=title_font)
            
            # Total countries
            draw.text((50, 80), f"Total Countries: {total_countries}", fill=(0, 0, 0), font=header_font)
            
            # Last refresh time
            refresh_text = f"Last Refreshed: {last_refresh.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            draw.text((50, 120), refresh_text, fill=(0, 0, 0), font=header_font)
            
            # Top 5 countries by GDP
            draw.text((50, 180), "Top 5 Countries by Estimated GDP:", fill=(0, 0, 0), font=header_font)
            
            y_position = 220
            for i, country in enumerate(top_countries, 1):
                gdp_formatted = f"${country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
                country_text = f"{i}. {country.name}: {gdp_formatted}"
                draw.text((70, y_position), country_text, fill=(0, 0, 0), font=text_font)
                y_position += 35
            
            # If no countries found
            if total_countries == 0:
                draw.text((50, 220), "No countries data available.", fill=(255, 0, 0), font=header_font)
            
            # Save image
            image.save(self.image_path)
            print(f"Summary image generated at: {self.image_path}")
            
            return True
            
        except Exception as e:
            print(f"Error generating summary image: {e}")
            return False

    def get_image_path(self):
        return self.image_path if os.path.exists(self.image_path) else None
