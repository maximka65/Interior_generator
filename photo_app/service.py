import os
import random

from photo_service import settings as conf


class MidJourneyIntegration:
    def __init__(self, uploaded_image_name, generation_type="creative", room_type="kitchen",
                 style="", facade_form="", hints=""):
        # modern -> modern minimalistic, neoclassic -> modern classic to our prompt
        # we left self.styles for navigation in the folders to search picture with realistic generation_type,
        # and we generated prompt with function __get_style_for_prompt()
        self.styles = ["classic", "modern", "neoclassic", "provence"]
        self.styles_for_prompt = ["classic", "modern minimalistic", "modern classic", "provence"]
        # we created function __get_room_type() for navigation in the folders to search
        # picture with realistic generation_type,
        # but we also created function __get_room_type_for_prompt() that gives us a common prompt
        self.room_types = ["bathroom", "bedroom", "closet", "hallway", "kitchen", "living_room"]
        self.generation_types = ["creative", "realistic"]
        self.facade_forms = ["corner_kitchen", "U-shaped_kitchen", "open_kitchen",
                             "kitchen-living_room"]  # adding if only user chose kitchen
        self.uploaded_image_name = uploaded_image_name
        self.generation_type = generation_type
        self.room_type = room_type
        self.style = style
        self.facade_form = facade_form
        self.hints = hints

    def get_midjourney_prompt(self):
        # prompt looking like:
        # <user_image_url> <prepared_image_url(if user chose realistic generation type)>
        # <room_type> + "clean" + <style_for_prompt(see comments upper)>
        # <facade_form(if user chose kitchen or not chose anything in room_type)>
        # <hints> furniture --s 0(if hints were not empty)
        midjourney_prompt = f'{self.__generate_user_image_url()} '
        if self.generation_type == 'realistic':
            midjourney_prompt += f'{self.__generate_saved_image_url()} '
        midjourney_prompt += f'{self.__get_room_type_for_prompt()} {self.__get_styles_for_prompt()} '
        # if self.__get_room_type() == "kitchen":
        #     midjourney_prompt += f'{self.facade_form} '
        if self.hints == "":
            return midjourney_prompt
        midjourney_prompt += f'{self.hints} furniture --s 0 '
        #rint(midjourney_prompt)
        return midjourney_prompt

    def __generate_saved_image_url(self):
        base_image_path = conf.SAVED_IMAGE_PATH
        room_type_ = self.__get_room_type()
        style_ = self.__get_style()

        room_type_and_style = os.path.join(room_type_, style_)

        saved_image_url = os.path.join(base_image_path, room_type_and_style)
        if self.facade_form != "":
            url = (conf.MAIN_DOMAIN, 'gstatic', 'photo_app', 'img', 'images_slon', room_type, style,
                    self.facade_form, self.__get_random_picture(saved_image_url))
        else:
            url = (conf.MAIN_DOMAIN, 'gstatic', 'photo_app', 'img', 'images_slon', room_type_, style_,
                self.__get_random_picture(saved_image_url))
        return '/'.join(url)

    def __generate_user_image_url(self):
        if (self.uploaded_image_name and self.uploaded_image_name != ""):
            url = (conf.MAIN_DOMAIN, 'media', 'temp', self.uploaded_image_name)
            return '/'.join(url)
        return ""

    def __get_style(self):
        if self.style != "":
            return self.style
        return random.choice(self.styles)

    def __get_styles_for_prompt(self):
        if self.style == "modern":
            return "modern minimalistic"
        elif self.style == "neoclassic":
            return "modern classic"
        elif self.style != "":
            return self.style

        return random.choice(self.styles_for_prompt)

    def __get_room_type(self):
        if self.room_type == "":
            return "kitchen"
        return self.room_type

    def __get_room_type_for_prompt(self):
        if self.room_type == "":
            return "kitchen clean"
        return f'{self.room_type} clean'

    def __get_random_picture(self, path):
        random_image = None

        if self.facade_form != "":
            path = os.path.join(path, self.facade_form)
        print(path, "PATH")
        #image_files = [f for f in os.listdir(path) if
        #               f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        image_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and
              f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]


        if image_files:
            random_image = random.choice(image_files)
        print(random_image)
        return random_image
