from django.utils.text import slugify


def generate_slug(instance, field, new_slug=None):

  slug = slugify(getattr(instance, field))

  return slug
