# Kaftar: Messenger Backend with MySQL and Elasticsearch

A command-line messaging application (inspired by Telegram) built as the term project for the **Database Systems** course at **Sharif University of Technology** (Fall 2018). Users can send private messages, create and join groups and channels, block users and manage their profiles. All data is stored in a relational **MySQL** database, and messages are also indexed in **Elasticsearch** for fast full-text and fuzzy search.

> *Kaftar* (کفتر) means "pigeon" in Persian, a nod to carrier pigeons.

## Highlights

- **Relational schema design (MySQL):** 11 tables for users, sessions, private, group and channel messages, memberships and blocked users, with primary and foreign keys.
- **Dual-write to SQL and NoSQL:** every message and membership is written to MySQL and indexed in Elasticsearch at the same time.
- **10 search queries in Elasticsearch:** full-text, fuzzy and date-based search across private chats, groups and channels, restricted to conversations the user belongs to.
- **Fast search:** every Elasticsearch query returned results in **1 to 3.2 ms on average** (5 runs each), much faster than the equivalent SQL search.

## Architecture

```
            ┌────────────────────┐
  user ───▶ │  src/main.py (CLI) │
            └─────────┬──────────┘
                      │ writes
           ┌──────────┴───────────┐
           ▼                      ▼
   ┌───────────────┐     ┌─────────────────────┐
   │     MySQL     │     │    Elasticsearch    │
   │ (source of    │     │ indices: message,   │
   │  truth)       │     │ membership (search) │
   └───────────────┘     └─────────────────────┘
```

## Database schema

| Table | Purpose |
|---|---|
| `KaftarUser` | Users (phone number, name, bio, password, self-destruct setting) |
| `UserSession` | Login sessions (device, IP, OS, first and last access) |
| `KaftarChannel`, `KaftarGroup` | Channels and groups with admin, link and bio |
| `PVMessage`, `GroupMessage`, `ChannelMessage` | Private, group and channel messages |
| `PVMembership`, `GroupMembership`, `ChannelMembership` | Who is in each conversation and when they last read it (used for unread counts) |
| `BlockedUser` | Block list |

The full schema is in [`schema.sql`](schema.sql).

## Commands

Type a command name followed by its arguments, one per line.

**Account:** `create_user <phone>`, `login <phone>`, `logout`, `set_name <name>`, `set_bio <bio>`, `set_password <password>`, `set_self_destruct <0-3>`

**Groups and channels:** `create_group <id> <name>`, `create_channel <id> <name>`, `set_group_link <id> <link>`, `set_channel_link <id> <link>`, `join_group <id>`, `join_channel <id>`, `join_link <link>`, `leave_group <id>`, `leave_channel <id>`

**Messaging:** `send_message <phone> <text>`, `send_message_group <id> <text>`, `send_message_channel <id> <text>`, `block_user <phone>`, `unblock_user <phone>`

**Viewing:** `home`, `count_unread`, `view_chat <phone>`, `view_group <id>`, `view_channel <id>`, `view_user_profile <phone>`, `view_group_profile <id>`, `view_channel_profile <id>`

**Search (Elasticsearch):**

| Command | What it does | Avg. time (ms) |
|---|---|---|
| `search_all <words>` | Full-text search across all of the user's chats, groups and channels | 3.0 |
| `search_all_fuzzy <words>` | Same, tolerant to typos (fuzzy matching) | 3.2 |
| `search_chat <phone> <words>` | Fuzzy search in a private chat | 1.2 |
| `search_group <id> <words>` | Fuzzy search in a group | 1.0 |
| `search_group_by_sender <id> <phone> <words>` | Fuzzy search for one member's messages in a group | 1.0 |
| `search_channel <id> <words>` | Fuzzy search in a channel | 1.0 |
| `view_messages_by_date <date>` | All of the user's messages on a date | 3.2 |
| `view_messages_by_date_chat <phone> <date>` | Messages in a private chat on a date | 2.0 |
| `view_messages_by_date_group <id> <date>` | Messages in a group on a date | 1.0 |
| `view_messages_by_date_channel <id> <date>` | Messages in a channel on a date | 1.2 |

Timings are from the project report, averaged over 5 runs ([table](docs/images/query_times.png)).

## Running it

Requirements: Python 3, MySQL 8 and Elasticsearch 6.x.

```bash
pip install -r requirements.txt

# 1. Create the database
mysql -u root -p < schema.sql

# 2. Start Elasticsearch 6.x (bin/elasticsearch, or bin\elasticsearch.bat on Windows)

# 3. Configure connection settings (see .env.example) and run
export KAFTAR_DB_PASSWORD=your_mysql_password
python src/main.py
```

Example session:

```
create_user 09120000001
login 09120000001
create_group g1 Friends
send_message_group g1 hello everyone
search_group g1 helo
```

Note: the program recreates the Elasticsearch indices each time it starts.

## Project structure

```
├── src/main.py              # CLI application: SQL logic and Elasticsearch indexing/search
├── schema.sql               # MySQL schema
├── requirements.txt
├── .env.example             # Connection settings
└── docs/
    ├── phase3_report_fa.pdf # Phase 3 report (Elasticsearch), in Persian
    └── images/query_times.png
```

## Team

Group project by **Bahar Jahani**, **Rozhin Nobahari** and **Amirhossein Bahrami**, Database Systems course, Sharif University of Technology, Fall 2018.
