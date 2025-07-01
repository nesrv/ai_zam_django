# Схема базы данных AI-ZAM

## ER-диаграмма

```mermaid
erDiagram
    %% Основные сущности строительной системы
    KategoriyaResursa {
        int id PK
        varchar nazvanie "Название категории"
    }
    
    Resurs {
        int id PK
        varchar naimenovanie "Наименование ресурса"
        varchar edinica_izmereniya "Единица измерения"
        int kategoriya_resursa_id FK "Категория ресурса"
    }
    
    Specialnost {
        int id PK
        varchar nazvanie "Название специальности"
    }
    
    Kadry {
        int id PK
        varchar fio "ФИО"
        int specialnost_id FK "Специальность"
        varchar razryad "Разряд"
        varchar pasport "Паспорт"
        varchar telefon "Телефон"
    }
    
    Objekt {
        int id PK
        varchar nazvanie "Название объекта"
        int otvetstvennyj_id FK "Ответственный"
        date data_nachala "Дата начала"
        date data_plan_zaversheniya "План завершения"
        date data_fakt_zaversheniya "Факт завершения"
        varchar status "Статус"
    }
    
    ResursyPoObjektu {
        int id PK
        int objekt_id FK "Объект"
        int resurs_id FK "Ресурс"
        decimal kolichestvo "Количество"
        decimal cena "Цена"
        decimal potracheno "Потрачено лимитов"
    }
    
    FakticheskijResursPoObjektu {
        int id PK
        int resurs_po_objektu_id FK "Ресурс по объекту"
    }
    
    RaskhodResursa {
        int id PK
        int fakticheskij_resurs_id FK "Фактический ресурс"
        date data "Дата"
        decimal izraskhodovano "Израсходовано"
    }
    
    %% AI и чат система
    AIModel {
        int id PK
        varchar name "Название модели"
        text description "Описание"
        datetime created_at "Дата создания"
        boolean is_active "Активна"
    }
    
    ChatSession {
        int id PK
        varchar session_id "ID сессии"
        int user_id FK "Пользователь"
        datetime created_at "Дата создания"
        datetime updated_at "Дата обновления"
        boolean is_active "Активна"
    }
    
    ChatMessage {
        int id PK
        int session_id FK "Сессия"
        varchar message_type "Тип сообщения"
        text content "Содержание"
        datetime created_at "Дата создания"
    }
    
    %% Telegram система
    TelegramUser {
        int id PK
        bigint telegram_id "Telegram ID"
        varchar username "Username"
        varchar first_name "Имя"
        varchar last_name "Фамилия"
        boolean is_active "Активен"
        datetime created_at "Дата регистрации"
        datetime updated_at "Дата обновления"
    }
    
    TelegramMessage {
        int id PK
        int user_id FK "Пользователь"
        varchar message_type "Тип сообщения"
        text content "Содержание"
        boolean is_from_user "От пользователя"
        datetime created_at "Дата создания"
    }
    
    %% Django Auth
    User {
        int id PK
        varchar username "Имя пользователя"
        varchar email "Email"
        boolean is_active "Активен"
        datetime date_joined "Дата регистрации"
    }
    
    %% Связи строительной системы
    KategoriyaResursa ||--o{ Resurs : "имеет"
    Resurs ||--o{ ResursyPoObjektu : "используется в"
    Objekt ||--o{ ResursyPoObjektu : "содержит"
    Kadry ||--o{ Objekt : "отвечает за"
    Specialnost ||--o{ Kadry : "имеет"
    ResursyPoObjektu ||--|| FakticheskijResursPoObjektu : "фактический"
    FakticheskijResursPoObjektu ||--o{ RaskhodResursa : "расходы по дням"
    
    %% Связи AI системы
    User ||--o{ ChatSession : "имеет сессии"
    ChatSession ||--o{ ChatMessage : "содержит сообщения"
    AIModel ||--o{ ChatMessage : "генерирует"
    
    %% Связи Telegram системы
    TelegramUser ||--o{ TelegramMessage : "отправляет/получает"
    User ||--o{ TelegramUser : "связан с"
```

## Диаграмма классов

```mermaid
classDiagram
    %% Основные классы строительной системы
    class KategoriyaResursa {
        +id: int
        +nazvanie: str
        +__str__()
    }
    
    class Resurs {
        +id: int
        +naimenovanie: str
        +edinica_izmereniya: str
        +kategoriya_resursa: FK
        +__str__()
    }
    
    class Specialnost {
        +id: int
        +nazvanie: str
        +__str__()
    }
    
    class Kadry {
        +id: int
        +fio: str
        +specialnost: FK
        +razryad: str
        +pasport: str
        +telefon: str
        +__str__()
    }
    
    class Objekt {
        +id: int
        +nazvanie: str
        +otvetstvennyj: FK
        +data_nachala: date
        +data_plan_zaversheniya: date
        +data_fakt_zaversheniya: date
        +status: str
        +__str__()
    }
    
    class ResursyPoObjektu {
        +id: int
        +objekt: FK
        +resurs: FK
        +kolichestvo: decimal
        +cena: decimal
        +potracheno: decimal
        +__str__()
    }
    
    class FakticheskijResursPoObjektu {
        +id: int
        +resurs_po_objektu: FK
        +__str__()
    }
    
    class RaskhodResursa {
        +id: int
        +fakticheskij_resurs: FK
        +data: date
        +izraskhodovano: decimal
        +__str__()
    }
    
    %% AI и чат классы
    class AIModel {
        +id: int
        +name: str
        +description: text
        +created_at: datetime
        +is_active: bool
        +__str__()
    }
    
    class ChatSession {
        +id: int
        +session_id: str
        +user: FK
        +created_at: datetime
        +updated_at: datetime
        +is_active: bool
        +__str__()
    }
    
    class ChatMessage {
        +id: int
        +session: FK
        +message_type: str
        +content: text
        +created_at: datetime
        +__str__()
    }
    
    %% Telegram классы
    class TelegramUser {
        +id: int
        +telegram_id: bigint
        +username: str
        +first_name: str
        +last_name: str
        +is_active: bool
        +created_at: datetime
        +updated_at: datetime
        +__str__()
    }
    
    class TelegramMessage {
        +id: int
        +user: FK
        +message_type: str
        +content: text
        +is_from_user: bool
        +created_at: datetime
        +__str__()
    }
    
    %% Связи
    KategoriyaResursa ||--o{ Resurs
    Resurs ||--o{ ResursyPoObjektu
    Objekt ||--o{ ResursyPoObjektu
    Kadry ||--o{ Objekt
    Specialnost ||--o{ Kadry
    ResursyPoObjektu ||--|| FakticheskijResursPoObjektu
    FakticheskijResursPoObjektu ||--o{ RaskhodResursa
    ChatSession ||--o{ ChatMessage
    TelegramUser ||--o{ TelegramMessage
```

## Описание таблиц

### Строительная система

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `kategoriya_resursa` | Категории ресурсов (кадры, материалы, механизмы) | `id`, `nazvanie` |
| `resurs` | Ресурсы (конкретные наименования) | `id`, `naimenovanie`, `kategoriya_resursa_id` |
| `specialnost` | Специальности кадров | `id`, `nazvanie` |
| `kadry` | Кадры (работники) | `id`, `fio`, `specialnost_id` |
| `objekt` | Строительные объекты | `id`, `nazvanie`, `otvetstvennyj_id`, `status` |
| `resursy_po_objektu` | Планируемые ресурсы по объектам | `id`, `objekt_id`, `resurs_id`, `kolichestvo`, `cena` |
| `fakticheskij_resurs_po_objektu` | Фактические ресурсы | `id`, `resurs_po_objektu_id` |
| `raskhod_resursa` | Расходы ресурсов по дням | `id`, `fakticheskij_resurs_id`, `data`, `izraskhodovano` |

### AI и чат система

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `ai_aimodel` | AI модели | `id`, `name`, `description` |
| `ai_chatsession` | Сессии чата | `id`, `session_id`, `user_id` |
| `ai_chatmessage` | Сообщения чата | `id`, `session_id`, `message_type`, `content` |

### Telegram система

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `telegrambot_telegramuser` | Пользователи Telegram | `id`, `telegram_id`, `username` |
| `telegrambot_telegrammessage` | Сообщения Telegram | `id`, `user_id`, `content`, `is_from_user` |

## Основные связи

1. **Объект → Ресурсы**: Один объект может иметь много ресурсов
2. **Ресурс → Категория**: Каждый ресурс принадлежит одной категории
3. **Кадры → Специальность**: Каждый кадр имеет одну специальность
4. **Объект → Ответственный**: Каждый объект может иметь одного ответственного
5. **Планируемые → Фактические ресурсы**: 1:1 связь
6. **Фактические ресурсы → Расходы**: 1:много связь по дням
7. **Пользователи → Сессии чата**: 1:много связь
8. **Сессии → Сообщения**: 1:много связь
9. **Telegram пользователи → Сообщения**: 1:много связь 