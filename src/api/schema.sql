create table
  public.potions (
    potion_id integer generated by default as identity,
    item_sku character varying not null,
    price integer null,
    red_ml integer null,
    blue_ml integer null default 0,
    green_ml integer null default 0,
    constraint potions_table_pkey primary key (potion_id)
  ) tablespace pg_default;

  create table
  public.potion_ledger_entries (
    id integer generated by default as identity,
    potion_id integer null,
    transaction_id integer null,
    quantity integer not null default 0,
    constraint potion_ledger_entries_pkey primary key (id),
    constraint potion_ledger_entries_potion_id_fkey foreign key (potion_id) references potions (potion_id),
    constraint potion_ledger_entries_transaction_id_fkey foreign key (transaction_id) references account_transactions (id)
  ) tablespace pg_default;

  create table
  public.carts (
    cart_id integer generated by default as identity,
    constraint carts_pkey primary key (cart_id)
  ) tablespace pg_default;

  create table
  public.cart_items (
    cart_item_id integer generated by default as identity,
    cart_id integer null,
    potion_id integer null,
    quantity integer null,
    constraint cart_items_pkey primary key (cart_item_id),
    constraint public_cart_items_cart_id_fkey foreign key (cart_id) references carts (cart_id),
    constraint public_cart_items_potion_id_fkey foreign key (potion_id) references potions (potion_id)
  ) tablespace pg_default;

  create table
  public.barrel_ledgers (
    id integer generated by default as identity,
    red_ml integer not null default 0,
    green_ml integer null default 0,
    blue_ml integer null default 0,
    constraint barrel_ledgers_pkey primary key (id)
  ) tablespace pg_default;
  create table
  public.accounts (
    account_id integer generated by default as identity,
    customer_name text not null,
    character_class text null,
    level integer null,
    constraint accounts_pkey primary key (account_id)
  ) tablespace pg_default;

  create table
  public.account_transactions (
    id integer generated by default as identity,
    created_at timestamp with time zone not null default now(),
    description character varying null,
    constraint account_transactions_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.account_ledger_entries (
    id integer generated by default as identity,
    account_id integer not null,
    account_transaction_id integer null,
    change integer null,
    constraint account_ledger_entries_pkey primary key (id),
    constraint account_ledger_entries_account_id_fkey foreign key (account_id) references accounts (account_id),
    constraint account_ledger_entries_account_transaction_id_fkey foreign key (account_transaction_id) references account_transactions (id)
  ) tablespace pg_default;