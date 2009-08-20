# coding:utf-8

import django.dispatch

pre_render_global_template = django.dispatch.Signal(providing_args=["request", "page_template"])
#post_render_global_template = django.dispatch.Signal(providing_args=["toppings", "size"])
