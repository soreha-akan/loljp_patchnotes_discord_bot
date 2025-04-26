CREATE TABLE articles (
	id serial4 NOT NULL,
	title varchar(100) NOT NULL,
	article_type int2 NOT NULL, -- 1: パッチノート (LoL) 2: パッチノート (TFT) 3:LoL公式ニュース 4: TFT公式ニュース
	url varchar(2048) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	modified_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	deleted bool DEFAULT false NOT NULL,
	deleted_at timestamp NULL,
	CONSTRAINT articles_article_type_check CHECK (((article_type >= 1) AND (article_type <= 8))),
	CONSTRAINT articles_pkey PRIMARY KEY (id)
);
CREATE INDEX articles_article_type_idx ON articles USING btree (article_type, url);
CREATE INDEX idx_articles_01 ON articles USING btree (url);

-- Column comments

COMMENT ON COLUMN articles.article_type IS '1: パッチノート (LoL) 2: パッチノート (TFT) 3:LoL公式ニュース 4: TFT公式ニュース';


CREATE TABLE notification_settings (
	id serial4 NOT NULL,
	channel_name varchar(100) NULL,
	channel_id numeric(30) NULL,
	guild_id numeric(30) NOT NULL,
	article_type int2 NOT NULL, -- 1: パッチノート (LoL) 2: パッチノート (TFT) 3:LoL公式ニュース 4: TFT公式ニュース
	is_active bool DEFAULT false NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	modified_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	deleted bool DEFAULT false NOT NULL,
	deleted_at timestamp NULL,
	CONSTRAINT notification_settings_article_type_check CHECK (((article_type >= 1) AND (article_type <= 8))),
	CONSTRAINT notification_settings_pkey PRIMARY KEY (id)
);
CREATE INDEX notification_settings_article_type_idx ON notification_settings USING btree (article_type, is_active);
CREATE INDEX notification_settings_guild_id_idx ON notification_settings USING btree (guild_id);

-- Column comments

COMMENT ON COLUMN notification_settings.article_type IS '1: パッチノート (LoL) 2: パッチノート (TFT) 3:LoL公式ニュース 4: TFT公式ニュース';

CREATE TABLE guilds (
	id serial4 NOT NULL,
	"name" varchar(100) NOT NULL,
	guild_id numeric(30) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	modified_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	deleted bool DEFAULT false NOT NULL,
	deleted_at timestamp NULL,
	CONSTRAINT guilds_guild_id_key UNIQUE (guild_id),
	CONSTRAINT guilds_pkey PRIMARY KEY (id)
);
CREATE INDEX guilds_guild_id_idx ON guilds USING btree (guild_id);