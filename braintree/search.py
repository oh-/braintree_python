class Search:
    class KeyValueNodeBuilder(object):
        def __init__(self, name):
            self.name = name

        def __eq__(self, value):
            return self.is_equal(value)

        def is_equal(self, value):
            return Search.Node(self.name, value)

        def __ne__(self, value):
            return self.is_not_equal(value)

        def is_not_equal(self, value):
            return Search.Node(self.name, not value)

    class TextNodeBuilder(object):
        def __init__(self, name):
            self.name = name

        def __eq__(self, value):
            return self.is_equal(value)

        def is_equal(self, value):
            return Search.Node(self.name, {"is": value})

        def __ne__(self, value):
            return self.is_not_equal(value)

        def is_not_equal(self, value):
            return Search.Node(self.name, {"is_not": value})

        def starts_with(self, value):
            return Search.Node(self.name, {"starts_with": value})

        def ends_with(self, value):
            return Search.Node(self.name, {"ends_with": value})

        def contains(self, value):
            return Search.Node(self.name, {"contains": value})

    class Node(object):
        def __init__(self, name, dict):
          self.name = name
          self.dict = dict

        def to_param(self):
            return self.dict

    class MultipleValueNodeBuilder(object):
        def __init__(self, name, whitelist = []):
            self.name = name
            self.whitelist = whitelist

        def in_list(self, list):
            invalid_args = set(list) - set(self.whitelist)
            if len(self.whitelist) > 0 and len(invalid_args) > 0:
                error_string = "Invalid argument(s) for %s: %s" % (self.name, ", ".join(invalid_args))
                raise AttributeError(error_string)
            return Search.Node(self.name, list)

        def __eq__(self, value):
            return self.in_list([value])

    class RangeNodeBuilder(object):
        def __init__(self, name):
            self.name = name

        def __ge__(self, min):
            return self.greater_than_or_equal_to(min)

        def greater_than_or_equal_to(self, min):
            return Search.Node(self.name, {"min": min})

        def __le__(self, max):
            return self.less_than_or_equal_to(max)

        def less_than_or_equal_to(self, max):
            return Search.Node(self.name, {"max": max})

        def between(self, min, max):
            return Search.Node(self.name, {"min": min, "max": max})