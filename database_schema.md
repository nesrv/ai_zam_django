# Схема базы данных AI-ZAM (Обновленная версия)

## ER-диаграмма

```mermaid
erDiagram
    %% AI Module
    AIModel {
        int id PK
        varchar name
        text description
        datetime created_at
        boolean is_active
    }

    %% Chat System
    ChatSession {
        int id PK
        varchar session_id UK
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

    %% Organizations and Staff
    Organizaciya {
        int id PK
        varchar nazvanie
        varchar inn UK
        boolean is_active
    }

    Podrazdelenie {
        int id PK
        int organizaciya_id FK
        varchar kod UK
        varchar nazvanie
    }

    Specialnost {
        int id PK
        varchar nazvanie
    }

    Sotrudnik {
        int id PK
        int organizaciya_id FK
        varchar fio
        date data_rozhdeniya
        varchar pol
        varchar razmer_odezhdy
        varchar razmer_obuvi
        varchar razmer_golovnogo_ubora
        int specialnost_id FK
        int podrazdelenie_id FK
        date data_priema
        date data_nachala_raboty
    }

    %% Documents and Templates
    DokumentySotrudnika {
        int id PK
        int sotrudnik_id FK
    }

    InstrukciiKartochki {
        int id PK
        int dokumenty_sotrudnika_id FK
        varchar nazvanie
        varchar shablon_instrukcii
        boolean soglasovan
        boolean raspechatn
        datetime data_sozdaniya
    }

    SotrudnikiShablonyProtokolov {
        int id PK
        varchar nomer_programmy
        varchar kurs
        varchar html_file
    }

    ProtokolyObucheniya {
        int id PK
        int sotrudnik_id FK
        int shablon_protokola_id FK
        date data_prikaza
        date data_protokola_dopuska
        date data_dopuska_k_rabote
        date data_ocherednoy_proverki
        varchar registracionnyy_nomer
        boolean raspechatn
    }

    Instruktazhi {
        int id PK
        int dokumenty_sotrudnika_id FK
        date data_instruktazha
        varchar vid_instruktazha
        text tekst_instruktazha
        varchar instruktor
        date data_ocherednogo_instruktazha
        boolean raspechatn
    }

    ShablonyDokumentovPoSpecialnosti {
        int id PK
        int specialnost_id FK
        varchar dolzhnostnaya_instrukciya
        varchar lichnaya_kartochka_rabotnika
        varchar lichnaya_kartochka_siz
        varchar karta_ocenki_riskov
        varchar instrukciya_po_ohrane_truda
    }

    %% Resources and Objects
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

    Objekt {
        int id PK
        varchar nazvanie
        int organizaciya_id FK
        varchar otvetstvennyj
        date data_nachala
        date data_plan_zaversheniya
        date data_fakt_zaversheniya
        varchar status
        boolean is_active
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

    DokhodResursa {
        int id PK
        int fakticheskij_resurs_id FK
        date data
        decimal vypolneno
    }

    SvodnayaRaskhodDokhodPoDnyam {
        int id PK
        int objekt_id FK
        date data
        decimal raskhod
        decimal dokhod
        decimal balans
    }

    KategoriyaPoObjektu {
        int id PK
        int objekt_id FK
        int kategoriya_id FK
    }

    %% Telegram Bot
    TelegramUser {
        int id PK
        bigint telegram_id UK
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

    TemporaryDocument {
        uuid id PK
        int user_id FK
        text content
        datetime created_at
    }

    %% Django Auth
    User {
        int id PK
        varchar username
        varchar email
        varchar first_name
        varchar last_name
        boolean is_active
        datetime date_joined
    }

    %% Relationships
    ChatSession ||--o{ ChatMessage : "has messages"
    User ||--o{ ChatSession : "creates sessions"
    
    Organizaciya ||--o{ Sotrudnik : "employs"
    Organizaciya ||--o{ Podrazdelenie : "has departments"
    Organizaciya ||--o{ Objekt : "owns projects"
    
    Specialnost ||--o{ Sotrudnik : "has specialty"
    Specialnost ||--|| ShablonyDokumentovPoSpecialnosti : "has templates"
    
    Podrazdelenie ||--o{ Sotrudnik : "belongs to"
    
    Sotrudnik ||--|| DokumentySotrudnika : "has documents"
    Sotrudnik ||--o{ ProtokolyObucheniya : "has protocols"
    
    DokumentySotrudnika ||--o{ InstrukciiKartochki : "contains instructions"
    DokumentySotrudnika ||--o{ Instruktazhi : "contains briefings"
    
    SotrudnikiShablonyProtokolov ||--|| ProtokolyObucheniya : "template for"
    
    KategoriyaResursa ||--o{ Resurs : "categorizes"
    KategoriyaResursa ||--o{ KategoriyaPoObjektu : "used in projects"
    
    Resurs ||--o{ ResursyPoObjektu : "allocated to"
    
    Objekt ||--o{ ResursyPoObjektu : "uses resources"
    Objekt ||--o{ SvodnayaRaskhodDokhodPoDnyam : "has daily summary"
    Objekt ||--o{ KategoriyaPoObjektu : "has categories"
    
    ResursyPoObjektu ||--|| FakticheskijResursPoObjektu : "actual usage"
    
    FakticheskijResursPoObjektu ||--o{ RaskhodResursa : "expenses"
    FakticheskijResursPoObjektu ||--o{ DokhodResursa : "income"
    
    TelegramUser ||--o{ TelegramMessage : "sends messages"
    TelegramUser ||--o{ TemporaryDocument : "generates documents"
```

## Описание таблиц

### Строительная система

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `kategoriya_resursa` | Категории ресурсов (кадры, материалы, механизмы) | `id`, `nazvanie` |
| `resurs` | Ресурсы (конкретные наименования) | `id`, `naimenovanie`, `kategoriya_resursa_id` |
| `object_specialnost` | Специальности кадров | `id`, `nazvanie` |
| `kadry` | Кадры (работники) | `id`, `fio`, `specialnost_id` |
| `objekt` | Строительные объекты | `id`, `nazvanie`, `otvetstvennyj_id`, `organizaciya_id`, `status` |
| `resursy_po_objektu` | Планируемые ресурсы по объектам | `id`, `objekt_id`, `resurs_id`, `kolichestvo`, `cena`, `potracheno` |
| `fakticheskij_resurs_po_objektu` | Фактические ресурсы | `id`, `resurs_po_objektu_id` |
| `raskhod_resursa` | Расходы ресурсов по дням | `id`, `fakticheskij_resurs_id`, `data`, `izraskhodovano` |
| `dokhod_resursa` | Доходы ресурсов по дням | `id`, `fakticheskij_resurs_id`, `data`, `vypolneno` |
| `kategoriya_po_objektu` | Категории по объектам | `id`, `kategoriya_id`, `objekt_id` |
| `svodnaya_raskhod_dokhod_po_dnyam` | Сводная по расходам/доходам | `id`, `objekt_id`, `data`, `raskhod`, `dokhod`, `balans` |

### Система сотрудников

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `sotrudniki_organizaciya` | Организации | `id`, `nazvanie`, `inn` |
| `sotrudniki_podrazdelenie` | Подразделения | `id`, `kod`, `nazvanie` |
| `sotrudniki_specialnost` | Специальности сотрудников | `id`, `nazvanie` |
| `sotrudniki_sotrudnik` | Сотрудники | `id`, `fio`, `data_rozhdeniya`, `organizaciya_id`, `podrazdelenie_id`, `specialnost_id` |
| `sotrudniki_dokumentysotrudnika` | Документы сотрудника | `id`, `sotrudnik_id` |
| `sotrudniki_instrukciikartochki` | Инструкции и карточки | `id`, `nazvanie`, `dokumenty_sotrudnika_id`, `file_path` |
| `sotrudniki_protokolyobucheniya` | Протоколы обучения | `id`, `nomer_programmy`, `nazvanie_kursa`, `dokumenty_sotrudnika_id` |
| `sotrudniki_instruktazhi` | Инструктажи | `id`, `data_instruktazha`, `vid_instruktazha`, `dokumenty_sotrudnika_id` |
| `sotrudniki_vidydokumentov` | Виды документов | `id`, `nazvanie`, `tip` |

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
| `telegrambot_temporarydocument` | Временные документы | `id`, `content`, `user_id` |

## Основные связи

### Строительная система
1. **Объект → Ресурсы**: Один объект может иметь много ресурсов
2. **Ресурс → Категория**: Каждый ресурс принадлежит одной категории
3. **Кадры → Специальность**: Каждый кадр имеет одну специальность
4. **Объект → Ответственный**: Каждый объект может иметь одного ответственного
5. **Объект → Организация**: Каждый объект принадлежит организации
6. **Планируемые → Фактические ресурсы**: 1:1 связь
7. **Фактические ресурсы → Расходы/Доходы**: 1:много связь по дням
8. **Объект → Категории**: Много ко многим через `kategoriya_po_objektu`

### Система сотрудников
9. **Организация → Сотрудники**: 1:много связь
10. **Подразделение → Сотрудники**: 1:много связь
11. **Специальность → Сотрудники**: 1:много связь
12. **Сотрудник → Документы**: 1:1 связь
13. **Документы → Инструкции/Протоколы/Инструктажи**: 1:много связь

### AI и чат система
14. **Пользователи → Сессии чата**: 1:много связь
15. **Сессии → Сообщения**: 1:много связь
16. **Telegram пользователи → Сообщения**: 1:много связь

## Новые возможности

### Управление сотрудниками
- Ведение личных дел сотрудников
- Управление документооборотом
- Протоколы обучения и инструктажи
- Привязка к организациям и подразделениям

### Доходная часть проектов
- Учет выполненных работ по дням
- Сопоставление доходов и расходов
- Сводная отчетность по балансу проекта

### Расширенная аналитика
- Детализация по категориям ресурсов
- Временные ряды доходов и расходов
- Контроль выполнения планов