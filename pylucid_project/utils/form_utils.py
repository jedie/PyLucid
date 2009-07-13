# coding:utf-8

def make_kwargs(data, keys):
    """
    Simple form util for transfer values from a dict.
    If you have a form for more than one model and you would like to easy get
    all needed key/values for the models.
    
    >>> POST = {1:"one", 2:"two", 3:"three"}
    >>> make_kwargs(POST, keys=[1,3])
    {1: 'one', 3: 'three'}
    >>> make_kwargs(POST, keys=[2,99])
    {2: 'two'}
    """
    kwargs = {}
    for key in keys:
        if key in data:
            kwargs[key] = data[key]
    return kwargs


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
