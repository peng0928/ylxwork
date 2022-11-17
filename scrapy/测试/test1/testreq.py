class A(object):
     bar = 1
     bar1 = 22


print(getattr(A(), 'bar1'))