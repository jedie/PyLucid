# coding: utf-8

def save_receiver(sender, **kwargs):
    """ signal post save handler -> create a new UpdateData entry """
    model_instance = kwargs["instance"]
    from models import PageUpdateListObjects
    PageUpdateListObjects.objects.add_entry(model_instance)
