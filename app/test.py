# import random
# list_text=[]
#
# for i in range(0,10):
#     list_text.append(random.randint(1,10))
#
# print(list_text)
#
# list_lt=[random.randint(1,10) for i in range(10)]
# print(list_lt)
# list=[i for i in range(1,101) if i%2==0]
# print(list)
# list1=[1,1,2,2,3,3,4,4,5,5]
# a=set(list1)
# print (a)
# list2=[]
# for i in list1:
#     list

# list1=[1,1,2,2,3,3,4,4,5,5]
# list2=[list1[0]]
# for i in list1:
#     if i not in list2:
#         list2.append(i)
# print(list2)

a=[1,2,3]
b=a
b.append(4)
c=a[:]
c.append(4)
a.append(b)
