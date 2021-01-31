-- SQLite
create table tickerinfo
(
tickercode varchar(20),
base_unit varchar(20),
quote_unit varchar(20),
low_price_24_hr integer,
high_price_24_hr integer,
last_trade_price integer,
mkt_open_price integer,
trade_volume_24_hr integer,
top_sell_price integer,
top_buy_price integer,
name varchar(255),
ticker_timestamp datetime,
refresh_timestamp datetime,
timezone varchar(50)
)