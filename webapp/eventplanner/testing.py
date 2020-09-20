# class Roles():
# yo 
#     def setname(self, name):
#         self.name = name

#     def getname():
#         return self.name


# role1 = Roles()
# role1.setname('Manager')
# print(role1.name)
# role2 = Roles()
# role2.setname('Moderator')
# print(role2.name)

# listofroles = []
# listofroles.append(role1)
# listofroles.append(role2)

# for role in listofroles:
#     if 'Manager' in role.name:
#         print('found')
# nuu = [x for x in range(1, 10)]
# print(nuu)
# class role1:
#     x = 1
#     name = ['Manager']


# class role2:
#     x = 2
#     name = ['Staff']


# class user:
#     y = 1
#     roles = [role1(), role2()]


# userme = user()
# # print(userme.roles[1].name)
# # for role in userme.roles:
# #     print(role.name)
# for role in userme.roles:
#     if 'Staff' in role.name:
#         print('found')
# class ticket:
#     def __init__(self, ticket_type, num_tickets, price):
#         self.ticket_type = ticket_type
#         self.num_tickets = num_tickets
#         self.price = price


# tickets = []
# ticket1 = ticket('ticket1', 22, 13)
# tickets.append(ticket1)
# for tik in tickets:
#     print(tik.ticket_type, tik.num_tickets, tik.price)
# ticket2 = ticket('ticket1', 27, 13)


# st = [1, 2, 3]
# pp = st.pop(2)
# print(pp)
# print(st)


ev_and_st = [(1, "not"), (1, "yes"), (1, "not"), (1, "yes")]
ll = []
for tp in ev_and_st:
    if tp not in ll:
        ll.append(tp)
print(ll)
