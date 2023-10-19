create or replace function set_updated_at() returns trigger
    language plpgsql as
$$
begin
    new.updated_at := current_timestamp;
    return new;
end;
$$;

create table texts
(
    code       text primary key,
    text       text not null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp
);
create trigger texts_updated_at
    before update
    on texts
    for each row
execute procedure set_updated_at();
comment on table texts is 'Статические тексты';
comment on column texts.code is 'Символьный код текста';
comment on column texts.text is 'Текст';


create table files
(
    code       text primary key,
    path       text not null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp
);
create trigger images_updated_at
    before update
    on files
    for each row
execute procedure set_updated_at();
comment on table files is 'Статические файлы';
comment on column files.code is 'Символьный код изображения';
comment on column files.path is 'Путь к файлу на диске';


create schema bot;

create table bot.chat_state
(
    chat_id    bigint primary key,
    state_code text not null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp
);
create trigger chat_state_updated_at
    before update
    on bot.chat_state
    for each row
execute procedure set_updated_at();
comment on table bot.chat_state is 'Состояния чатов';
comment on column bot.chat_state.chat_id is 'Идентификатор чата';
comment on column bot.chat_state.state_code is 'Код состояния чата';

create table bot.chat_context
(
    chat_id    bigint primary key,
    context    jsonb not null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp
);
create trigger chat_context_updated_at
    before update
    on bot.chat_context
    for each row
execute procedure set_updated_at();
comment on table bot.chat_context is 'Контекст чатов';
comment on column bot.chat_context.chat_id is 'Идентификатор чата';
comment on column bot.chat_context.context is 'Контекст чата';
