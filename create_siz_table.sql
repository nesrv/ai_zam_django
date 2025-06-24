CREATE TABLE specodezhda_siz (
    id INT PRIMARY KEY IDENTITY(1,1),
    nazvanie NVARCHAR(255) NOT NULL,
    edinica_izmereniya NVARCHAR(50) NOT NULL
);

INSERT INTO specodezhda_siz (nazvanie, edinica_izmereniya) VALUES
('Каска защитная', 'шт'),
('Респиратор', 'шт'),
('Перчатки рабочие', 'пара'),
('Очки защитные', 'шт'),
('Комбинезон', 'шт'),
('Сапоги резиновые', 'пара'),
('Жилет сигнальный', 'шт'),
('Наушники защитные', 'шт'),
('Маска сварочная', 'шт'),
('Пояс страховочный', 'шт');