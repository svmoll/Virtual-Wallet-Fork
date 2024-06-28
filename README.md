# MyPyWallet: Virtual Wallet API

## Description:
Back-end web application designed to help users manage their finances efficiently. It allows users to send and receive money, manage their cards, and perform various transactions seamlessly. The application supports user-to-user transactions.

Features

- **User Management:** Register, login, and profile management for both regular users and admins.
- **Cards:** Add and view cards with personalized designs.
- **Transactions:** Perform, confirm, deny, and view transactions with detailed history and categorization.
- **Recurring Transactions:** Set up and manage automatic, recurring transactions.
- **Contacts:** Create and manage a list of contacts for easy money transfers.
- **Categories:** Create, edit, and delete transaction categories for better expense tracking and viewing category statistics.
- **Admin Features:** Approve registrations, block/unblock users, and manage user transactions.
- **Notifications:** Email verification and notifications for failed transactions.

## Installation

### Prerequisites

Make sure you have the following software installed on your system:

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Steps

**Clone the Repository**

   Clone the project repository from GitHub to your local machine.

   ```bash
   git clone https://github.com/K-I-S/Virtual-Wallet.git
   cd Virtual-Wallet
   ```
**Create and Activate a Virtual Environment**

It's a good practice to use a virtual environment to manage your project dependencies.
```bash
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```
**Install Dependencies**

Install the necessary Python packages using the provided requirements.txt file.

```bash
pip install -r requirements.txt
```

**Setup the Database**

Ensure that your database is configured correctly. You may need to modify the config.py file under app/core/ with your database settings. After configuring, populate the database.

```bash
python app/core/db_population.py
```
**Run the Application**

Navigate to the main application directory and run the main.py file.

This should start the server, and the API will be available at http://localhost:8000.

### Swagger documentation: http://127.0.0.1:8000/redoc

## 1. Register User 

Registers a new user with the system.

### Request

- **Method:** `POST`
- **Path:** `/users/register`

#### Request Body

- **Content Type:** `application/json`

| Field        | Type   | Description                                                                                                                                                 |
|--------------| ------ |-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| username     | string | The username of the user (unique identifier).                                                                                                               |
| email        | string | The email address of the user (unique identifier).                                                                                                          |
| password     | string | The password for the user's account. (has to be atleast 8 and max 20 symbols and should contain capital letter, digit, and special symbol (+, -, *, &, ^, …) |
| phone_number | string | The phone number of the user.                                                                                                                               |
| fullname     | string | The fullname of the user.                                                                                                                                   |

### Response

- **Status Code:** `201 Created`
- **Body:** Confirmation message with the created username.

## 2. User Login

Logs in a user to the system and generates an authentication token.

### Request

- **Method:** `POST`
- **Path:** `/users/login`

#### Request Body

- **Content Type:** `application/json`

| Field     | Type   | Description                                  |
| --------- | ------ | -------------------------------------------- |
| username  | string | The username of the user.                    |
| password  | string | The password for the user's account.         |

### Response

- **Status Code:** `200 OK`
- **Body:** JSON containing the access token and token type.

## 3. User Logout

Logs out a user and invalidates the current authentication token.

### Request

- **Method:** `GET`
- **Path:** `/users/logout`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** Confirmation message for successful logout.

## 4. View User Profile

Retrieves the profile information of the current user.

### Request

- **Method:** `GET`
- **Path:** `/users/view`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing user profile information.

## 5. Update User Profile

Updates the profile information of the current user.

### Request

- **Method:** `PUT`
- **Path:** `/users/update`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field     | Type   | Description                                  |
| --------- | ------ | -------------------------------------------- |
| firstname | string | The new first name of the user.              |
| lastname  | string | The new last name of the user.               |
| email     | string | The new email address of the user.           |

### Response

- **Status Code:** `200 OK`
- **Body:** Confirmation message with the updated username.

## 6. Search User

Searches for a user by username, email, or phone number.

### Request

- **Method:** `GET`
- **Path:** `/users/search`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter   | Type   | Description                                  |
| ----------- | ------ | -------------------------------------------- |
| username    | string | The username to search for.                  |
| email       | string | The email to search for.                     |
| phone_number| string | The phone number to search for.              |

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing the found user's information.

## 7. Add Contact

Adds a new contact to the current user's contact list.

### Request

- **Method:** `POST`
- **Path:** `/users/contacts`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field     | Type   | Description                                  |
| --------- | ------ | -------------------------------------------- |
| username  | string | The username of the contact to add.          |

### Response

- **Status Code:** `200 OK`
- **Body:** Confirmation message for successfully adding the contact.

## 8. Delete Contact

Deletes a contact from the current user's contact list.

### Request

- **Method:** `DELETE`
- **Path:** `/users/contacts`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field     | Type   | Description                                  |
| --------- | ------ | -------------------------------------------- |
| username  | string | The username of the contact to delete.       |

### Response

- **Status Code:** `204 No Content`

## 9. View Contacts

Retrieves the contact list of the current user.

### Request

- **Method:** `GET`
- **Path:** `/users/view/contacts`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter | Type   | Description                                  |
| --------- | ------ | -------------------------------------------- |
| page      | int    | The page number for pagination.              |
| limit     | int    | The number of contacts per page.             |

### Response

- **Status Code:** `200 OK`
- **Body:** JSON array containing the list of contacts or a message if no contacts are found.


## 10. Admin: Search Users

Searches for users by username, email, or phone number with pagination support.

### Request

- **Method:** `GET`
- **Path:** `/admin/search/users`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter    | Type   | Description                                  |
| ------------ | ------ | -------------------------------------------- |
| username     | string | The username to search for.                  |
| email        | string | The email to search for.                     |
| phone_number | string | The phone number to search for.              |
| page         | int    | The page number for pagination.              |
| limit        | int    | The number of users per page.                |

### Response

- **Status Code:** `200 OK`
- **Body:** JSON array containing the list of users found.

## 11. Admin: Change User Status

Changes the status of a user.

### Request

- **Method:** `PUT`
- **Path:** `/admin/status`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field     | Type   | Description                                  |
| --------- | ------ | -------------------------------------------- |
| username  | string | The username of the user to change status.   |

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing the action taken.

## 12. Admin: View Transactions

Retrieves transactions with optional filters for sender, receiver, status, flagged status, and sort order.

### Request

- **Method:** `GET`
- **Path:** `/admin/view/transactions`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter   | Type   | Description                                  |
| ----------- | ------ | -------------------------------------------- |
| sender      | string | The username of the sender.                  |
| receiver    | string | The username of the receiver.                |
| status      | string | The status of the transaction.               |
| flagged     | string | Flagged transactions (accepts 'yes' or 'no').|
| sort        | string | The sort order of the transactions.          |
| page        | int    | The page number for pagination.              |
| limit       | int    | The number of transactions per page.         |

### Response

- **Status Code:** `200 OK`
- **Body:** JSON array containing the list of transactions or a message if no transactions are found.

## 13. Admin: Deny Transaction

Denies a transaction.

### Request

- **Method:** `PUT`
- **Path:** `/admin/deny/transactions`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter       | Type   | Description                   |
| --------------- | ------ | ----------------------------- |
| transaction_id  | int    | The ID of the transaction.     |

### Response

- **Status Code:** `204 No Content`

## 14. Admin: Confirm User

Confirms a user's access.

### Request

- **Method:** `PUT`
- **Path:** `/admin/confirm/users`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter | Type   | Description          |
| --------- | ------ | -------------------- |
| user_id   | int    | The ID of the user.  |

### Response

- **Status Code:** `200 OK`
- **Body:** Confirmation message for granting user access.

## 15. Deposit Money

Allows the user to deposit a specified amount into their account.

### Request

- **Method:** `POST`
- **Path:** `/deposit`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field          | Type    | Description                              |
| -------------- | ------- | ---------------------------------------- |
| deposit_amount | decimal | The amount of money to deposit.          |

### Response

- **Status Code:** `201 Created`
- **Body:** JSON object containing a message with the updated account balance.


## 16. Withdraw Money

Allows the user to withdraw a specified amount from their account.

### Request

- **Method:** `POST`
- **Path:** `/withdrawal`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field             | Type    | Description                              |
| ----------------- | ------- | ---------------------------------------- |
| withdrawal_amount | decimal | The amount of money to withdraw.         |

### Response

- **Status Code:** `201 Created`
- **Body:** JSON object containing a message with the updated account balance.


## 17. Create Draft Transaction

Creates a draft transaction for the current user.

### Request

- **Method:** `POST`
- **Path:** `/draft`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field        | Type   | Description                   |
| ------------ | ------ | ----------------------------- |
| transaction  | object | The transaction details.      |

### Response

- **Status Code:** `201 Created`
- **Body:** JSON object containing a message about the draft transaction details.

## 18. Edit Draft Transaction

Edits an existing draft transaction for the current user.

### Request

- **Method:** `PUT`
- **Path:** `/{transaction_id}`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field              | Type   | Description                   |
| ------------------ | ------ | ----------------------------- |
| updated_transaction| object | The updated transaction details.|

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing a message about the updated draft transaction details.

## 19. Confirm Transaction

Confirms a draft transaction for the current user.

### Request

- **Method:** `POST`
- **Path:** `/{transaction_id}/confirm`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing a message about the pending transfer details.

## 20. Delete Draft Transaction

Deletes a draft transaction for the current user.

### Request

- **Method:** `DELETE`
- **Path:** `/{transaction_id}`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `204 No Content`
- **Body:** No content.

## 21. Accept Transaction

Accepts an incoming transaction for the current user.

### Request

- **Method:** `POST`
- **Path:** `/{transaction_id}/accept`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing a message about the updated balance.

## 22. Decline Transaction 

Declines an incoming transaction for the current user.

### Request

- **Method:** `POST`
- **Path:** `/{transaction_id}/decline`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `204 No Content`
- **Body:** No content.

## 23. Create a Recurring Transaction

Creates a recurring transaction for the current user.

### Request

- **Method:** `POST`
- **Path:** `/recurring_transactions/`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field                  | Type   | Description                      |
| ---------------------- | ------ | -------------------------------- |
| recurring_transaction  | object | The recurring transaction details.|

### Response

- **Status Code:** `201 Created`
- **Body:** JSON object confirming the creation of the recurring transaction.

## 24. Display Recurring Transactions

Displays the list of recurring transactions for the current user.

### Request

- **Method:** `GET`
- **Path:** `/recurring_transactions/`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing the list of recurring transactions, or a message if there are no recurring transactions.

## 25. Cancel Recurring Transaction

Cancels a recurring transaction for the current user.

### Request

- **Method:** `DELETE`
- **Path:** `/recurring_transactions/`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter                  | Type | Description                       |
| -------------------------- | ---- | --------------------------------- |
| recurring_transaction_id   | int  | The ID of the recurring transaction to cancel.|

### Response

- **Status Code:** `204 No Content`
- **Body:** No content.


## 26. Create Card

Creates a new card for the current user.

### Request

- **Method:** `POST`
- **Path:** `/`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `201 Created`
- **Body:** JSON object containing a message confirming the creation of a new card for the user.

## 27. View User's Cards

Retrieves the list of cards associated with the current user.

### Request

- **Method:** `GET`
- **Path:** `/`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing a message and the list of cards associated with the user. If no cards are associated, the response contains a message indicating this.

## 28. Delete Card

Deletes a specified card of the current user.

### Request

- **Method:** `DELETE`
- **Path:** `/{id}`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK` (if deletion is successful), `400 Bad Request` (if the card does not belong to the user)
- **Body:** JSON object containing a message confirming the deletion of the card, or an error message if the card does not belong to the user.

## 29. Create Category

Creates a new category for the current user.

### Request

- **Method:** `POST`
- **Path:** `/`

#### Headers

- **Authorization:** `Bearer <token>`

#### Request Body

- **Content Type:** `application/json`

| Field    | Type   | Description             |
| -------- | ------ | ----------------------- |
| category | object | The category to create. |

### Response

- **Status Code:** `201 Created`
- **Body:** JSON object containing a message confirming the creation of the new category with its name and ID.

## 30. View User's Categories

Retrieves the list of categories associated with the current user.

### Request

- **Method:** `GET`
- **Path:** `/list`

#### Headers

- **Authorization:** `Bearer <token>`

### Response

- **Status Code:** `200 OK`
- **Body:** JSON object containing a message and the list of categories associated with the user. If no categories are associated, the response contains a message indicating this.

## 31. Create Expense Report

Generates a report of the user's expenses within a specified date range.

### Request

- **Method:** `GET`
- **Path:** `/report`

#### Headers

- **Authorization:** `Bearer <token>`

#### Query Parameters

| Parameter | Type | Description                       |
| --------- | ---- | --------------------------------- |
| from_date | date | The start date for the report.    |
| to_date   | date | The end date for the report.      |

### Response

- **Status Code:** `201 Created` (if the report is successfully generated), `204 No Content` (if the report could not be generated)
- **Body:** JSON object containing a message indicating whether the report was successfully generated.





## File Architecture
![Screenshot_20240609_080751](https://github.com/K-I-S/Virtual-Wallet/assets/155480916/daf4dbe8-dcce-47fa-85a9-dc466b623dbe)



## Database Architecture
![Screenshot_20240610_123502](https://github.com/K-I-S/Virtual-Wallet/assets/155480916/d3106fa0-7dd2-42c2-a595-0a33355145e7)
