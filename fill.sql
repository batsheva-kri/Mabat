
INSERT INTO products(name,image_path,category_id, status,information,preferred_supplier_id) VALUES('אואזיס צילינדר','../../../images/oazis toric',1,'inventory','',2);
INSERT INTO products(name,image_path,category_id, status,information,preferred_supplier_id) VALUES('ביופיניטי','../../../images/ciofinity',1,'inventory','',2);
INSERT INTO products(name,image_path,category_id, status,information,preferred_supplier_id) VALUES('ביופיניטי צילינדר','../../../images/biofinity toric',1,'inventory','',2);
INSERT INTO products(name,image_path,category_id, status,information,preferred_supplier_id) VALUES('קליר','../../../images/clear',1,'inventory','',2);
INSERT INTO products(name,image_path,category_id, status,information,preferred_supplier_id) VALUES('סופלנס','../../../images/soflens',1,'inventory','',2);
INSERT INTO products(name,image_path,category_id, status,information,preferred_supplier_id) VALUES('ביו מדיקס','../../../images/biomedics',1,'inventory','',2);
ALTER TABLE customer_invitations ADD COLUMN delivery_requested INTEGER DEFAULT 0; -- 0 לא, 1 כן
ALTER TABLE customer_invitations ADD COLUMN delivery_sent INTEGER DEFAULT 0; 
ALTER TABLE customer_invitations
    ADD COLUMN curvature REAL CHECK (curvature IN (8.4, 8.5, 8.6, 8.7, 8.8, 8.9));

ALTER TABLE customer_invitations
    ADD COLUMN prescription TEXT CHECK (prescription IN ('עדשות','משקפיים'));
