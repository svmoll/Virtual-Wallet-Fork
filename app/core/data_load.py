from sqlalchemy.orm import Session
from api.models.models import User, Contacts, Cards, Transactions, Categories
from core.database import engine


#Users
admin = User(username="admin", password="adminADMIN123", email="admin@admin.com", phone_number="0888111111")
user = User(username="user", password="userUSER123", email="user@user.com", phone_number="0888222222")
julia_roberts = User(username="JuliaRoberts", password="JuliaRoberts", email="julia@roberts.com", phone_number="0888222222")
tom_hanks = User(username="TomHanks", password="TomHanks", email="tom@hanks.com", phone_number="0888222222")


# #Contacts
# user_contacts = Contacts(user_username = user, contact_username = julia_roberts)
# user_contacts = Contacts(user_username = user, contact_username = tom_hanks)


# #Accounts
# account_1 = Accounts(username = user, )


users_to_load = [admin, user]
data_load = users_to_load


def data_load():
    with Session(engine) as session:
        session.add_all(data_load)
        session.commit()
        session.refresh(data_load)


# Run the data_load function
# if __name__ == "__main__":
#     data_load()