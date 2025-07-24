import time


def get_object_with_retry(model, retries=3, delay=2, **attrs):
    for _ in range(retries):
        try:
            return model.objects.get(**attrs)
        except model.DoesNotExist:
            time.sleep(delay * retries)
    raise model.DoesNotExist(f"Subscription plan {attrs} not found")
