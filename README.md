# **amazun bookstöre**

![logo, copyright infingement intended](Assets/Img/fancy_logo.png)

SQL Project for <a href="https://github.com/wlinds/ITHS-AI22-RDBMS">ITHS SQL & DB course</a>. *Now unionized!*


Notes available to read here: [devlog](notes.ipynb)


# **Setup for MSSQL Server 2017**

## 0. Install ODBC Driver
Instructions <a href="https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16">here.</a>

## 1. Use Docker to create Microsoft™ SQL-server
Here we will name it *microsuft* as an example.

```
docker run -d --name microsuft -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=superSafe123' -e 'MSSQL_USER_UID=10001' -e 'MSSQL_USER_GID=10001' -p 1433:1433 mcr.microsoft.com/mssql/server:2017-latest

````
Replace *microsuft* and *superSafe123* with your own choice, or keep as is.

This will create an new MSSQL Server.

**Troubleshooting:**\
To check if everything runs correctly:
```
docker logs microsuft
```


## 2. Create the **amazun** database.

Either use mssql-cli or any RDBMS (Azure Data Studio/SQL Server Management Studio) and run:

```
CREATE DATABASE amazun;
```

## 3. Check connection string

In <code>models.py</code> there is a connection string:

````
cstring2 = "mssql+pyodbc://SA:superSafe123@localhost:1433/amazun?driver=ODBC+Driver+17+for+SQL+Server"
````

Update the password in this string if you changed it in step 1.

## 4. Run main.py

>⚠️ **TODO:** There is a bug with get_dummy_books() which will cause the very first runtime to fail. Every instance after first run of main.py will work correctly.
I'll have to look into this.

This will create the following data structue and fill it with some pickled dummy data:

![Alt text](dbschema.png)


main.py will then continue to run the webscraper located at <code>Scripts/author_crawler.py</code> indefinitely.

>⚠️ **TODO:** Fix constraints and many-to-many relations.


# **Running the webapp**
After the above setup has been completed, we can run the webapp.

## 1. Head over to **app.py** to create your login:

```
if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)

    with app.app_context():
        db.create_all()
        create_user('admin2', 'supersafe') <-- Change to your own credentials
```

1. Run app.py and visit http://127.0.0.1:5000 to browse the store locally.

![Alt text](example-store.png)

>⚠️ **TODO:** Improve CSS.