# Will Robison, Christian Yoder, Paris Ward, Harley Sigmon, Hunter Johansen
# This program takes sales data from an excel file, creates a dataframe, and then uploads to a database
# The user can then search by category and receive summaries and graphs of the information

# LIBRARIES
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plot
import psycopg2


df = pd.read_excel('Retail_Sales_Data.xlsx')

# Info to connect with database
username = 'postgres'
password = input("What is your postgres password? ")
host = 'localhost'
port = '5432'
database = 'IS303'

# Create the connection string to speak with the is303 database
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

# Establish the connection to the database and store to variable
conn = engine.connect()

# Overwrite the dataframe data to a table called sales
df.to_sql('sale', conn, if_exists='replace', index=False)

# Loop that continues until user enters something other than 1 or 2
while True:
    choice = input("If you want to import data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ")

    # PART 1
    if choice == '1' : 
        # Fix Name column
        split_names  = df["name"].str.split("_", expand = True)
        df.insert(1,"first_name",split_names[0])
        df.insert(2,"last_name",split_names[1])
        df.drop(columns=['name'], inplace=True)

        # Fix Category column
        productCategoriesDict = {
                'Camera': 'Technology',
                'Laptop': 'Technology',
                'Gloves': 'Apparel',
                'Smartphone': 'Technology',
                'Watch': 'Accessories',
                'Backpack': 'Accessories',
                'Water Bottle': 'Household Items',
                'T-shirt': 'Apparel',
                'Notebook': 'Stationery',
                'Sneakers': 'Apparel',
                'Dress': 'Apparel',
                'Scarf': 'Apparel',
                'Pen': 'Stationery',
                'Jeans': 'Apparel',
                'Desk Lamp': 'Household Items',
                'Umbrella': 'Accessories',
                'Sunglasses': 'Accessories',
                'Hat': 'Apparel',
                'Headphones': 'Technology',
                'Charger': 'Technology'}
        df["category"] = df["product"].map(productCategoriesDict)

        # Save the results as a table called ‘sale’ in your is303 postgres database.
        df.to_sql('sale', conn, if_exists='replace', index=False)

        print("You've imported the excel file into your postgres database.")

    # PART 2
    elif choice == '2' :  
        print("The following are all the categories that have been sold:")
        
        # Finds each unique category
        query = "SELECT DISTINCT category FROM sale ORDER BY category;"
        
        # Goes through each category and lists it out
        categories_df = pd.read_sql( text(query), conn)

        lst_categories = []
        for iCount, category in enumerate(categories_df['category'], start=1):
            # Displays the counter and the value for the category
            print(f"{iCount}: {category}")

            # appends category to list which is used later to call category names when searching database
            lst_categories.append(category)
            
        # Allows user to enter category choice to learn more about
        category_choice = int(input("Please enter the number of the category you want to see summarized: "))
        category_name = lst_categories[category_choice - 1]

        # Sends query to database and updates df
        query = """
            SELECT product, SUM(total_price) AS total_sales, AVG(total_price) AS average_sales, SUM(quantity_sold) AS quantity_sold
            FROM sale
            WHERE category = :category
            GROUP BY product"""

        df = pd.read_sql( text(query), conn, params={"category": category_name})

        # Prints out total sales, average sale amount, and total units sold
        print(f"Sum of total sales: {round(df['total_sales'].sum(),2)}")
        print(f"Average sale amount: {round(df['average_sales'].mean(),2)}")
        print(f"Total units sold: {round(df['quantity_sold'].sum(),0)}")

        # creating the chart
        plot.figure(figsize=(10, 6))

        plot.bar(df['product'], df['total_sales'])

        # adds title to the top of the chart
        plot.title(f"Total Sales in {category_name}")

        # label for the x-axis
        plot.xlabel("Product") 

        # label for the y-axis 
        plot.ylabel("Total Sales")  
     
        # Formats chart
        plot.xticks(rotation=45)
        plot.tight_layout()

        # Display the chart
        plot.show()


    else : 
        print("Closing the program")
        break