# My Recipebook
#### Video Demo:  <URL HERE>
#### Description:

<br>

## Background

I wanted to create a recipebook where I could keep track of recipes in order to prepare before cooking. I used the same concept as the Problem set 9 Finance so it is a web-based application using JavaScript, Python, and SQL.
<P> I borrowed the functions of login and register pages as well as the error page. However the rest was built from scratch and I used bootstrap to give the site a fresh look.
I will go through the pages with the codes one by one.

<br>

## Homepage (index.html)

Once the user logged in they will be able to access to the homepage where there are six different links at the top of the page. Working from left to right, "My Recipebook" is the first link and it is to redirect the user back to this page. The following links "Dishes", "Recipes", "Measurements" will be explained later but the user is able to have quick access to them at any parts of the whole site.
<P>
The next part is a bit interesting as it's where the user can see their username displayed. I used some Jinja code in the layout page.

`{{session.user_name|capitalize}}`

In the application.py, I saved the user's name by add this from line 194.

`session["user_name"] = rows[0]["username"]` 

I believe it one of the easiest ways to gain access to a global variable via FLASK. Hopefully this won't create any security loopholes as the user will only have access to their own username and not others.

The next link would be redirecting the user to the "profile.html" page where are able to change password. Again, this was part of Pset9 assignment that I carried over to this project. 

## User's Fridge (myfridge.html)

The first thing the user can see is a table listing all the ingredients, quantity and expiry date respectively. I used SQL to help keep track of the database. 

`fridges = db.execute("SELECT * FROM fridge WHERE id = ? ORDER BY date", session["user_id"])` 

This code was used to catch the data and passed it via returning the value “fridges”.

`return render_template("myfridge.html", fridges = fridges)`

On the HTML side, I used Jinja coding and create a for loop.

`{% for fridge in fridges %}`

and called each item by their names

`{{fridge['ingredients']}}
{{fridge['qty']}}
{{fridge['date']}}`

The next part is the input from the
 user. I used the request get function from the FLASK side.

 `ingr = request.form.get("ingredients")`
Once the user entered all the information, they can click submit button and it will be updated to the database via this code

`db.execute("INSERT INTO fridge (id,ingredients, qty, date) VALUES (?,?,?,?)", user,ingr ,qty ,date)`

There are also some error checking

`if not request.form.get("ingredients"):
                return apology("Must provide ingredients")`

Another feature on this page is that all expired ingredients will be highlight thanks to Javascript.

`function Expired()`

I got the current date and compared with the expiry date. If the expiry date is before the current one, then the function will highlight the row.

There is another function where the user can remove any expired ingredients and Javascript with JSON came to play. The highlighted rows information will be sent via JSON and from the FLASK side, the following code updated the database.

`db.execute("DELETE FROM fridge WHERE (id,ingredients, qty, date) = (?,?,?,?)", user,ingr,qty ,date)`

## Measurements (measurements.html)

This is where I used Javascript to dynamically change the measurements and temperature. The functions of `temperatureConverter`, `weightConverter` and `volConverter`. 

All functions do the same job which is grab the number from textbox `document.getElementById` and by using a formula, the user can see the changes.

## Recipes (receipes.html)


The user can input the recipes from the bottom of the page in a table format. It starts out with 5 rows but the user can add more rows by clicking the "Add more ingredients" button. Another Javascript code is used here to make the magic happen.

`function addTableRow()`

## Dishes (dishes.html)

The search box is the first thing displayed on this page. 
With `function myFunction`, the user can type any keyword in the table at the bottom and then it will start to filter out the list.

Finally the user can click on the name of the dish and they will be redirected to the recipe page with that particular dish.

`<td><a id="link" href="/receipes#{{dish['id']}}">{{dish['dish']}} </a></td>
            <td>{{dish['cuisine']}} </td>`
