from rest_framework.routers import DefaultRouter


class CustomRouter(DefaultRouter):
    def get_lookup_regex(self, viewset, lookup_prefix=''):
        base_regex = super().get_lookup_regex(viewset, lookup_prefix)
        lookup_field = getattr(viewset, 'lookup_field', None)

        if lookup_field and lookup_field != 'pk':
            return r'(?P<{lookup_prefix}{lookup_field}>[-\w]+)'.format(
                lookup_prefix=lookup_prefix,
                lookup_field=lookup_field
            )
        return base_regex

    def get_routes(self, viewset):
        routes = super().get_routes(viewset)
        lookup_field = getattr(viewset, 'lookup_field', None)

        if lookup_field and lookup_field != 'pk':
            for route in routes:
                if '{lookup_field}' in route.url:
                    route.url = route.url.replace(
                        '{lookup_field}',
                        f'{{{lookup_field}}}'
                    )

        return routes
