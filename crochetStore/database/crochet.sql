

-- ============================================
-- STEP 2: CREATE TABLES (dbo format)
-- ============================================

CREATE TABLE [dbo].[Users] (
    [user_id] INT IDENTITY(1,1) PRIMARY KEY,
    [name] VARCHAR(100) NOT NULL,
    [email] VARCHAR(100) UNIQUE NOT NULL,
    [phone] VARCHAR(20),
    [password] VARCHAR(255) NOT NULL,
    [role] VARCHAR(20) CHECK ([role] IN ('admin', 'staff', 'customer')) NOT NULL,
    [created_at] DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE [dbo].[Category] (
    [cat_id] INT IDENTITY(1,1) PRIMARY KEY,
    [categoryName] VARCHAR(100) NOT NULL
);
GO

CREATE TABLE [dbo].[Items] (
    [item_id] INT IDENTITY(1,1) PRIMARY KEY,
    [itemName] VARCHAR(100) NOT NULL,
    [basePrice] DECIMAL(10,2) NOT NULL
);
GO

CREATE TABLE [dbo].[ItemsQuant] (
    [itemQuant_id] INT IDENTITY(1,1) PRIMARY KEY,
    [item_id] INT NOT NULL,
    [color] VARCHAR(50),
    [stock] INT,
    [description] VARCHAR(255),
    FOREIGN KEY ([item_id]) REFERENCES [dbo].[Items]([item_id])
);
GO

CREATE TABLE [dbo].[SubCategory] (
    [subcat_id] INT IDENTITY(1,1) PRIMARY KEY,
    [cat_id] INT NOT NULL,
    [item_id] INT NOT NULL,
    [subCatName] VARCHAR(100),
    FOREIGN KEY ([cat_id]) REFERENCES [dbo].[Category]([cat_id]),
    FOREIGN KEY ([item_id]) REFERENCES [dbo].[Items]([item_id])
);
GO

CREATE TABLE [dbo].[Address] (
    [addr_id] INT IDENTITY(1,1) PRIMARY KEY,
    [province] VARCHAR(100),
    [city] VARCHAR(100),
    [area] VARCHAR(100),
    [houseNumber] VARCHAR(100)
);
GO

CREATE TABLE [dbo].[UserAddress] (
    [user_id] INT NOT NULL,
    [addr_id] INT NOT NULL,
    PRIMARY KEY ([user_id], [addr_id]),
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[Users]([user_id]),
    FOREIGN KEY ([addr_id]) REFERENCES [dbo].[Address]([addr_id])
);
GO

CREATE TABLE [dbo].[Orders] (
    [order_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL,
    [staff_id] INT NULL,
    [addr_id] INT NOT NULL,
    [totalPrice] DECIMAL(10,2),
    [paymentMethod] VARCHAR(50),
    [order_status] VARCHAR(50),
    [order_date] DATETIME DEFAULT GETDATE(),
    [dispatch_date] DATETIME NULL,
    [trackingID] VARCHAR(50),
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[Users]([user_id]),
    FOREIGN KEY ([staff_id]) REFERENCES [dbo].[Users]([user_id]),
    FOREIGN KEY ([addr_id]) REFERENCES [dbo].[Address]([addr_id])
);
GO

CREATE TABLE [dbo].[OrderItems] (
    [orderItem_id] INT IDENTITY(1,1) PRIMARY KEY,
    [order_id] INT NOT NULL,
    [itemQuant_id] INT NOT NULL,
    [quantity] INT,
    [price] DECIMAL(10,2),
    FOREIGN KEY ([order_id]) REFERENCES [dbo].[Orders]([order_id]),
    FOREIGN KEY ([itemQuant_id]) REFERENCES [dbo].[ItemsQuant]([itemQuant_id])
);
GO

CREATE TABLE [dbo].[Cart] (
    [cart_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL,
    [itemQuant_id] INT NOT NULL,
    [quantity] INT,
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[Users]([user_id]),
    FOREIGN KEY ([itemQuant_id]) REFERENCES [dbo].[ItemsQuant]([itemQuant_id])
);
GO

CREATE TABLE [dbo].[Wishlist] (
    [wishlist_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL,
    [itemQuant_id] INT NOT NULL,
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[Users]([user_id]),
    FOREIGN KEY ([itemQuant_id]) REFERENCES [dbo].[ItemsQuant]([itemQuant_id])
);
GO

CREATE TABLE [dbo].[Complaint] (
    [complaint_id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL,
    [description] VARCHAR(255),
    [status] VARCHAR(50),
    [created_at] DATETIME DEFAULT GETDATE(),
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[Users]([user_id])
);
GO

-- ============================================
-- STEP 3: VERIFY TABLES CREATED
-- ============================================
--SELECT * FROM sys.tables;
--GO
