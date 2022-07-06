drop table if exists users;
create table users
(
    id             bigint auto_increment,
    user_id        bigint           not null,
    first_name     varchar(255)     null,
    last_name      varchar(255)     null,
    username       varchar(255)     null,
    phone          varchar(100)     null,
    kicked         bit default b'0' null,
    root           bit default b'0' not null,
    bash_execution bit default b'0' not null,
    constraint id
        unique (id),
    constraint user_id
        unique (user_id)
);

alter table users
    add primary key (id);





drop table if exists bot_groups;

create table bot_groups
(
    id        bigint auto_increment,
    group_name varchar(255) null,
    group_id  bigint       not null,
    constraint chat_name
        unique (group_name),
    constraint group_id
        unique (group_id),
    constraint id
        unique (id)
);

alter table bot_groups
    add primary key (id);








drop table if exists users_in_groups;

create table users_in_groups
(
    id          bigint unsigned auto_increment,
    group_id    bigint           not null,
    user_id     bigint           not null,
    kicked      bit default b'0' not null,
    group_admin bit default b'0' not null,
    constraint id
        unique (id),
    constraint users_in_groups_ibfk_1
        foreign key (group_id) references bot_groups (id)
            on delete cascade,
    constraint users_in_groups_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade,
    constraint uq_group_user unique (group_id, user_id)
);

create index group_id
    on users_in_groups (group_id);

create index user_id
    on users_in_groups (user_id);

alter table users_in_groups
    add primary key (id);







drop table if exists bot_user_private_chats;

create table bot_user_private_chats
(
    id               bigint unsigned auto_increment,
    user_id          bigint null,
    telegram_chat_id bigint null,
    constraint id
        unique (id),
    constraint telegram_chat_id
        unique (telegram_chat_id),
    constraint user_id
        unique (user_id),
    constraint bot_user_private_chats_ibfk_1
        foreign key (user_id) references users (id)
            on delete cascade
);

alter table bot_user_private_chats
    add primary key (id);





drop table if exists last_invite_link;

create table last_invite_link
(
    id         bigint unsigned auto_increment,
    link       varchar(255)                       not null,
    group_id   bigint                             not null,
    updated_at datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint group_id_2
        unique (group_id),
    constraint id
        unique (id),
    constraint last_invite_link_ibfk_1
        foreign key (group_id) references bot_groups (id)
            on delete cascade
);

create index group_id
    on last_invite_link (group_id);

alter table last_invite_link
    add primary key (id);
