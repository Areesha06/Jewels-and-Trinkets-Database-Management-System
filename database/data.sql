-- ============================
-- 1. USERS
-- ============================
INSERT INTO Users (name, email, phone, password, role, created_at)
VALUES
('Areesha Kashif', 'areesha@example.com', '03001234567', 'hashed_pwd1', 'customer', '2025-01-10'),
('Fatima Noor', 'fatima@example.com', '03119876543', 'hashed_pwd2', 'customer', '2025-02-05'),
('Ali Raza', 'ali@example.com', '03221234567', 'hashed_pwd3', 'staff', '2025-03-15'),
('Sara Ahmed', 'sara@example.com', '03339876543', 'hashed_pwd4', 'admin', '2025-01-01');

-- ============================
-- 2. CATEGORY
-- ============================
INSERT INTO Category (categoryName)
VALUES
('Home Decor'),
('Accessories'),
('Toys');

-- ============================
-- 3. ITEMS
-- ============================
INSERT INTO Items (itemName, basePrice)
VALUES
('Crochet Blanket', 2500),
('Woolen Hat', 1200),
('Amigurumi Teddy', 1800),
('Crochet Bag', 2200),
('Table Mat Set', 1500);

-- ============================
-- 4. SUBCATEGORY
-- ============================
-- Note: assumes cat_id and item_id auto-assigned sequentially (1..n)
INSERT INTO SubCategory (cat_id, item_id, subCatName)
VALUES
(1, 1, 'Blankets'),
(2, 2, 'Winter Wear'),
(3, 3, 'Stuffed Toys'),
(2, 4, 'Bags'),
(1, 5, 'Dining Decor');

-- ============================
-- 5. ITEMSQUANT (Color Variants)
-- ============================
INSERT INTO ItemsQuant (item_id, color, stock, description)
VALUES
(1, 'Cream White', 10, 'Soft crochet blanket with floral pattern'),
(1, 'Sky Blue', 7, 'Baby blanket made from hypoallergenic yarn'),
(2, 'Red', 15, 'Warm woolen hat with pom pom'),
(2, 'Grey', 12, 'Chunky wool hat for winter'),
(3, 'Brown', 8, 'Handmade teddy with safety eyes'),
(4, 'Beige', 5, 'Crochet bag with wooden handles'),
(5, 'Multicolor', 20, 'Set of 4 round table mats with coasters');

-- ============================
-- 6. ADDRESS
-- ============================
INSERT INTO [Address] (province, city, area, houseNumber)
VALUES
('Sindh', 'Karachi', 'Gulshan-e-Iqbal', 'House 24A'),
('Punjab', 'Lahore', 'DHA Phase 5', 'House 16B'),
('Sindh', 'Karachi', 'PECHS', 'Flat 12C'),
('Punjab', 'Islamabad', 'G-11', 'House 89');

-- ============================
-- 7. USERADDRESS
-- ============================
-- Uses auto-generated user_id and addr_id (assumes same insertion order)
INSERT INTO UserAddress (user_id, addr_id)
VALUES
(1, 1),
(1, 3),
(2, 2),
(3, 4);

-- ============================
-- 8. ORDERS
-- ============================
INSERT INTO Orders (user_id, staff_id, addr_id, totalPrice, paymentMethod, order_status, order_date, dispatch_date, trackingID)
VALUES
(1, 3, 1, 3700, 'Cash on Delivery', 'Delivered', '2025-03-01', '2025-03-03', 'TRK12345'),
(2, 3, 2, 1800, 'Card', 'Shipped', '2025-04-15', '2025-04-17', 'TRK54321');

-- ============================
-- 9. ORDERITEMS
-- ============================
INSERT INTO OrderItems (order_id, itemQuant_id, quantity, price)
VALUES
(1, 1, 1, 2500),
(1, 3, 1, 1200),
(2, 5, 1, 1800);

-- ============================
-- 10. CART
-- ============================
INSERT INTO Cart (user_id, itemQuant_id, quantity)
VALUES
(1, 4, 1),
(2, 2, 1),
(2, 6, 1);

-- ============================
-- 11. WISHLIST
-- ============================
INSERT INTO Wishlist (user_id, itemQuant_id)
VALUES
(1, 6),
(1, 7),
(2, 1);

-- ============================
-- 12. COMPLAINT
-- ============================
INSERT INTO Complaint (user_id, description, status, created_at)
VALUES
(1, 'Received wrong color of blanket', 'Resolved', '2025-03-05'),
(2, 'Delayed delivery', 'Pending', '2025-04-20');
