CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    rule_string TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES rules(id) ON DELETE CASCADE,
    node_type VARCHAR(50) NOT NULL, 
    left_node INTEGER, 
    right_node INTEGER, 
    value TEXT, 
    FOREIGN KEY (left_node) REFERENCES nodes(id),
    FOREIGN KEY (right_node) REFERENCES nodes(id)
);
