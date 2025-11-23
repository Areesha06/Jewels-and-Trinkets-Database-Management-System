
DECLARE 
    @user_id INT = 1,
    @item_id INT = 1,
    @itemQuant_id INT = 1,
    @email VARCHAR(100) = 'demo@example.com',
    @password VARCHAR(100) = 'password123',
    @name VARCHAR(100) = 'Areesha',
    @price DECIMAL(10,2) = 1200.00,
    @stock INT = 25,
    @desc VARCHAR(255) = 'Soft crochet wool item',
    @cat_id INT = 2,
    @subject VARCHAR(100) = 'Inquiry',
    @message VARCHAR(255) = 'I love your products!',
    @zone_name VARCHAR(100) = 'Karachi South',
    @rate DECIMAL(10,2) = 250.00;

------------------------------------------------------------
-- CUSTOMER SCREENS
------------------------------------------------------------

-- 1. HOME PAGE – Featured products & promotions
SELECT TOP 5 item_id, itemName, basePrice
FROM dbo.Items
ORDER BY item_id DESC;

SELECT * 
FROM dbo.Category;

-- 2. SHOP – Product Catalog by Category
SELECT i.item_id, i.itemName, i.basePrice, c.categoryName
FROM dbo.Items i
JOIN dbo.SubCategory s ON i.item_id = s.item_id
JOIN dbo.Category c ON s.cat_id = c.cat_id
WHERE c.categoryName = 'Accessories';

-- 3. PRODUCT DETAILS PAGE
SELECT i.item_id, i.itemName, i.basePrice, q.color, q.stock, q.description
FROM dbo.Items i
JOIN dbo.ItemsQuant q ON i.item_id = q.item_id
WHERE i.item_id = @item_id;

-- 4. CART PAGE
SELECT c.cart_id, i.itemName, q.color, c.quantity, (i.basePrice * c.quantity) AS total
FROM dbo.Cart c
JOIN dbo.ItemsQuant q ON c.itemQuant_id = q.itemQuant_id
JOIN dbo.Items i ON q.item_id = i.item_id
WHERE c.user_id = @user_id;

-- 5. CHECKOUT PAGE
SELECT a.addr_id, a.province, a.city, a.area, a.houseNumber
FROM dbo.UserAddress ua
JOIN dbo.Address a ON ua.addr_id = a.addr_id
WHERE ua.user_id = @user_id;

-- 6. WISHLIST PAGE
SELECT w.wishlist_id, i.itemName, q.color, i.basePrice
FROM dbo.Wishlist w
JOIN dbo.ItemsQuant q ON w.itemQuant_id = q.itemQuant_id
JOIN dbo.Items i ON q.item_id = i.item_id
WHERE w.user_id = @user_id;

-- 7. LOGIN / REGISTER PAGE
SELECT user_id, name, role
FROM dbo.Users
WHERE email = @email AND password = @password;

INSERT INTO dbo.Users (name, email, password, role, created_at)
VALUES (@name, @email, @password, 'customer', GETDATE());

-- 8. MY ACCOUNT – Profile & Orders
SELECT name, email, phone, role 
FROM dbo.Users
WHERE user_id = @user_id;

SELECT o.order_id, o.order_date, o.order_status, SUM(oi.price * oi.quantity) AS total
FROM dbo.Orders o
JOIN dbo.OrderItems oi ON o.order_id = oi.order_id
WHERE o.user_id = @user_id
GROUP BY o.order_id, o.order_date, o.order_status;

-- 9. CONTACT & ABOUT PAGE (demo table not defined, just an example)
-- INSERT INTO dbo.Contact (name, email, subject, message, created_at)
-- VALUES (@name, @email, @subject, @message, GETDATE());


------------------------------------------------------------
-- ADMIN / STAFF SCREENS
------------------------------------------------------------

-- 10. ADMIN DASHBOARD
SELECT * FROM dbo.Orders WHERE order_status = 'Pending';

SELECT i.itemName, q.stock
FROM dbo.ItemsQuant q
JOIN dbo.Items i ON q.item_id = i.item_id
WHERE q.stock < 10;

SELECT SUM(oi.price * oi.quantity) AS daily_revenue
FROM dbo.Orders o
JOIN dbo.OrderItems oi ON o.order_id = oi.order_id
WHERE CAST(o.order_date AS DATE) = CAST(GETDATE() AS DATE);

SELECT TOP 10 order_id, user_id, order_date, order_status
FROM dbo.Orders
ORDER BY order_date DESC;

-- 11. ORDERS MANAGEMENT
SELECT o.order_id, u.name AS customer, o.order_status, o.order_date, SUM(oi.price * oi.quantity) AS total
FROM dbo.Orders o
JOIN dbo.Users u ON o.user_id = u.user_id
JOIN dbo.OrderItems oi ON o.order_id = oi.order_id
GROUP BY o.order_id, u.name, o.order_status, o.order_date;

-- 12. PRODUCT MANAGEMENT
INSERT INTO dbo.Items (itemName, basePrice)
VALUES (@name, @price);

UPDATE dbo.ItemsQuant
SET stock = @stock, description = @desc
WHERE itemQuant_id = @itemQuant_id;

DELETE FROM dbo.Items WHERE item_id = @item_id;

-- 13. USER MANAGEMENT
SELECT user_id, name, email, role, created_at 
FROM dbo.Users;

SELECT u.user_id, u.name, u.email, a.city, a.area
FROM dbo.Users u
JOIN dbo.UserAddress ua ON u.user_id = ua.user_id
JOIN dbo.Address a ON ua.addr_id = a.addr_id
WHERE u.user_id = @user_id;

-- 14. REPORTS
SELECT SUM(oi.price * oi.quantity) AS total_sales, COUNT(DISTINCT o.order_id) AS total_orders
FROM dbo.Orders o
JOIN dbo.OrderItems oi ON o.order_id = oi.order_id;

SELECT TOP 5 i.itemName, SUM(oi.quantity) AS total_sold
FROM dbo.OrderItems oi
JOIN dbo.ItemsQuant q ON oi.itemQuant_id = q.itemQuant_id
JOIN dbo.Items i ON q.item_id = i.item_id
GROUP BY i.itemName
ORDER BY total_sold DESC;

SELECT SUM(i.basePrice * q.stock) AS total_inventory_value
FROM dbo.Items i
JOIN dbo.ItemsQuant q ON i.item_id = q.item_id;
