# encoding: utf-8

"""
    i18n utilities
    ~~~~~~~~~~~~~~
    
    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


def filter_by_language(values_list, prefered_languages_pk):
    """
    Filter existing items with client prefered languages. 
    
    values_list is like this: queryset.values_list("pk", "entry", "language")
    
    returns a list if ids, usage e.g.:
        used_content = self.model.objects.filter(pk__in=used_ids)
    
    Note: In this DocTest we have change the prefered_languages_pk numbers
    to strings, for better understanding:
    
    >>> values_list = [
    ...    (7, 5, "en"), (6, 5, "de"),
    ...    (1, 4, "en"), (2, 4, "de"), (5, 4, "es"),
    ...    (3, 3, "en"), (8, 3, "es"),
    ...    (9, 1, "en"), (10, 1, "xx"),
    ...    (4, 2, "en")
    ... ]
    >>> filter_by_language(values_list, ("de", "en"))
    [9, 4, 3, 2, 6]

    >>> filter_by_language(values_list, ("en", "de"))
    [9, 4, 3, 1, 7]

    >>> filter_by_language(values_list, ("xx", "en"))
    [10, 4, 3, 1, 7]

    >>> filter_by_language(values_list, ("es", "en", "de"))
    [9, 4, 8, 5, 7]

    >>> filter_by_language(values_list, ("de", "es", "en"))
    [9, 4, 8, 2, 6]
    """
    # Group language & content by entry
    entry_dict = {}
    for content_id, entry_id, language_id in values_list:
        if entry_id not in entry_dict:
            entry_dict[entry_id] = [(language_id, content_id)]
        else:
            entry_dict[entry_id].append((language_id, content_id))


    # Create a list of content id's which the best language match
    used_ids = []
    for existing_entries in entry_dict.values():
        temp_content_dict = dict(existing_entries)
        for prefered in prefered_languages_pk:
            if prefered in temp_content_dict:
                used_ids.append(temp_content_dict[prefered])
                break

    return used_ids


if __name__ == "__main__":
    import doctest
    print doctest.testmod()
    print "DocTest end."
