create table categories(
    codename_id varchar(255) primary key,
    name varchar(255),
    nominations text,
    base_expense boolean
);

insert into categories (codename_id, name, nominations, base_expense)
values
    ("products", "продукти", "їжа, консерви, корм, продовольчі запаси, street-food, fast-food, стрит-фуд, фаст-фуд, доставка, напівфабріканти, газові напої, спеції, олія, сіль", true),
    ("coffee", "кава, чай", "кава, кофеїн, кавові вироби, кофейні зерна, чай, гарячі напої", true),
    ("dinner", "сніданок/обід/вечеря або будь-яке приймання їжі", "обід, вечеря, сніданок, ресторан, їдальня, ланч, кафе, піцирія", true),
    ("transport", "транспорт", "метро, таксі, автобус, тралейбус, трамвай, бензин", false),
    ("phone/connection", "телефонія", "телефон, зв'язок, тариф", false),
    ("books", "книги", "література, книги, комікси, журнали, публіцистика", false),
    ("internet/devices", "інтернет та девайси", "інтернет, ремонт, поклейка скла, чохол, новий девайс", false),
    ("subscriptions", "підписки", "підписка, підписки", false),
    ("other", "будь-щось інше", "табак, алкоголь, медікаменти, битова хімія", true);

create table budget(
    codename varchar(250) primary key,
    is_set boolean,
    daily_limit integer
);

insert into budget(codename, is_set, daily_limit) values ('base', TRUE, 500);

create table expense(
    id integer primary key,
    amount integer,
    created datetime,
    category_codename integer,
    raw_text text,
    FOREIGN KEY(category_codename) REFERENCES categories(codename_id)
);