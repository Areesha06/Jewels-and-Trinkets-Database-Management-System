-- Show all available crochet items with stock and color
SELECT I.itemName, IQ.color, IQ.stock, IQ.description, I.basePrice
FROM Items I
JOIN ItemsQuant IQ ON I.item_id = IQ.item_id
WHERE IQ.stock > 0;

--Show items by category and subcategory
SELECT C.categoryName, S.subCatName, I.itemName, I.basePrice
FROM Category C
JOIN SubCategory S ON C.cat_id = S.cat_id
JOIN Items I ON S.item_id = I.item_id
ORDER BY C.categoryName, S.subCatName;


--View items in a user’s cart
SELECT C.cart_id, I.itemName, IQ.color, C.quantity, I.basePrice, 
       (C.quantity * I.basePrice) AS totalPrice
FROM Cart C
JOIN ItemsQuant IQ ON C.itemQuant_id = IQ.itemQuant_id
JOIN Items I ON IQ.item_id = I.item_id
WHERE C.user_id = 1  

--Calculate total cart value for checkout
SELECT SUM(C.quantity * I.basePrice) AS cartTotal
FROM Cart C
JOIN ItemsQuant IQ ON C.itemQuant_id = IQ.itemQuant_id
JOIN Items I ON IQ.item_id = I.item_id
WHERE C.user_id = 1

--Show all orders placed by a customer
SELECT O.order_id, O.totalPrice, O.paymentMethod, O.order_status, 
       O.order_date, O.trackingID
FROM Orders O
WHERE O.user_id = 1;


--Show items within a specific order
SELECT I.itemName, IQ.color, OI.quantity, OI.price
FROM OrderItems OI
JOIN ItemsQuant IQ ON OI.itemQuant_id = IQ.itemQuant_id
JOIN Items I ON IQ.item_id = I.item_id
WHERE OI.order_id = 1;


--View all complaints by a user
SELECT complaint_id, description, status, created_at
FROM Complaint
WHERE user_id = 1
ORDER BY created_at DESC

--Staff/admin view of unresolved complaints
SELECT C.complaint_id, U.name, C.description, C.status, C.created_at
FROM Complaint C
JOIN Users U ON C.user_id = U.user_id
WHERE C.status = 'Pending'

--Display user details with role
SELECT name, email, phone, role, created_at
FROM Users
WHERE user_id = 1

--Show all addresses linked to a user
SELECT A.province, A.city, A.area, A.houseNumber
FROM UserAddress UA
JOIN Address A ON UA.addr_id = A.addr_id
WHERE UA.user_id = 1;

--View stock levels of all item variants
SELECT I.itemName, IQ.color, IQ.stock
FROM Items I
JOIN ItemsQuant IQ ON I.item_id = IQ.item_id
ORDER BY I.itemName;


--Find low-stock items (for restocking alerts)
SELECT I.itemName, IQ.color, IQ.stock
FROM Items I
JOIN ItemsQuant IQ ON I.item_id = IQ.item_id
WHERE IQ.stock < 5

--Show all items in user’s wishlist
SELECT I.itemName, IQ.color, I.basePrice
FROM Wishlist W
JOIN ItemsQuant IQ ON W.itemQuant_id = IQ.itemQuant_id
JOIN Items I ON IQ.item_id = I.item_id
WHERE W.user_id = 1;


--Count how many users have a certain item in wishlist
SELECT I.itemName, COUNT(W.user_id) AS wishlistCount
FROM Wishlist W
JOIN ItemsQuant IQ ON W.itemQuant_id = IQ.itemQuant_id
JOIN Items I ON IQ.item_id = I.item_id
GROUP BY I.itemName
ORDER BY wishlistCount DESC;

