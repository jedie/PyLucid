

module_name = "PyBB_forum_cfg"


module = __import__(
    module_name,
    globals(), locals(),
    [module_name]
)


for i in dir(module): print i
print module