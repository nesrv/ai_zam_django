# Схема базы данных AI-ZAM (Исправленная версия)

## ER-диаграмма

```mermaid
erDiagram
    KategoriyaResursa {
        int id PK
        varchar nazvanie
    }
    
    Resurs {
        int id PK
        varchar naimenovanie
        varchar edinica_izmereniya
        int kategoriya_resursa_id FK
    }
    
    Specialnost {
        int id PK
        varchar nazvanie
    }
    
    Kadry {
        int id PK
        varchar fio
        int specialnost_id FK
        varchar razryad
        varchar pasport
        varchar telefon
    }
    
    Objekt {
        int id PK
        varchar nazvanie
        int otvetstvennyj_id FK
        date data_nachala
        date data_plan_zaversheniya
        date data_fakt_zaversheniya
        varchar status
    }
    
    ResursyPoObjektu {
        int id PK
        int objekt_id FK
        int resurs_id FK
        decimal kolichestvo
        decimal cena
        decimal potracheno
    }
    
    FakticheskijResursPoObjektu {
        int id PK
        int resurs_po_objektu_id FK
    }
    
    RaskhodResursa {
        int id PK
        int fakticheskij_resurs_id FK
        date data
        decimal izraskhodovano
    }
    
    AIModel {
        int id PK
        varchar name
        text description
        datetime created_at
        boolean is_active
    }
    
    ChatSession {
        int id PK
        varchar session_id
        int user_id FK
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    ChatMessage {
        int id PK
        int session_id FK
        varchar message_type
        text content
        datetime created_at
    }
    
    TelegramUser {
        int id PK
        bigint telegram_id
        varchar username
        varchar first_name
        varchar last_name
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    TelegramMessage {
        int id PK
        int user_id FK
        varchar message_type
        text content
        boolean is_from_user
        datetime created_at
    }
    
    User {
        int id PK
        varchar username
        varchar email
        boolean is_active
        datetime date_joined
    }
    
    KategoriyaResursa ||--o{ Resurs : "имеет"
    Resurs ||--o{ ResursyPoObjektu : "используется в"
    Objekt ||--o{ ResursyPoObjektu : "содержит"
    Kadry ||--o{ Objekt : "отвечает за"
    Specialnost ||--o{ Kadry : "имеет"
    ResursyPoObjektu ||--|| FakticheskijResursPoObjektu : "фактический"
    FakticheskijResursPoObjektu ||--o{ RaskhodResursa : "расходы по дням"
    User ||--o{ ChatSession : "имеет сессии"
    ChatSession ||--o{ ChatMessage : "содержит сообщения"
    User ||--o{ TelegramUser : "связан с"
    TelegramUser ||--o{ TelegramMessage : "отправляет/получает"
```

## Диаграмма классов

```mermaid
classDiagram
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

## Упрощенная схема связей

```mermaid
graph TD
    A[KategoriyaResursa] --> B[Resurs]
    B --> C[ResursyPoObjektu]
    D[Objekt] --> C
    E[Kadry] --> D
    F[Specialnost] --> E
    C --> G[FakticheskijResursPoObjektu]
    G --> H[RaskhodResursa]
    
    I[User] --> J[ChatSession]
    J --> K[ChatMessage]
    I --> L[TelegramUser]
    L --> M[TelegramMessage]
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style I fill:#e8f5e8
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