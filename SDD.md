### **第1章 引言**

#### **1.1 文档目的**

本文档旨在为“智慧水利展示系统”课程项目提供详细的软件设计说明。其主要目的包括：

- **定义系统架构**：详细描述系统的整体结构、组件划分及各组件间的交互关系。
- **指导开发实现**：作为后续编码、测试和集成阶段的权威技术蓝图，确保开发过程有章可循。
- **明确设计约束**：阐明系统采用的技术栈、数据流和接口设计，为项目评审和验收提供依据。
- **便于后续维护**：为系统的理解、维护和未来可能的功能扩展提供技术文档支持。
  本文档的目标读者是项目开发人员、测试人员以及课程指导教师。

#### **1.2 系统范围**

本系统是一个面向课程设计的B/S（浏览器/服务器）架构的智慧水利展示平台。

- **本系统包含以下核心功能模块：**
  - **后端服务层**：
    1. **API网关**：基于FastAPI和SQLModel构建，提供所有前端请求的RESTful API接口，负责业务逻辑处理。
    2. **数据持久化系统**：基于SQLite数据库，负责水利相关数据（如水位、流量、工程信息等）的存储与管理。
    3. **信息获取系统**：基于Scrapy框架与定时任务（如APScheduler），自动化地从指定的公开水利信息网站爬取数据，并存入数据库。
  - **前端展示层**：
    1. **技术框架**：基于Vue.js、Element Plus组件库和ECharts图表库构建的单页面Web应用。
    2. **核心模块**：包含用户登录与管理、水利数据综合看板、地理信息地图展示、历史数据查询与分析等主要功能页面。
- **本系统明确不包含以下内容：**
  - 物理硬件传感器数据的直接采集。
  - 任何形式的移动端（Android/iOS）原生应用程序开发。
  - 对非公开或需要高级权限访问的水利数据的获取。

#### **1.3 定义、首字母缩写词和缩略语**

| 术语/缩写 | 全称                              | 解释                                 |
| :-------- | :-------------------------------- | :----------------------------------- |
| SDD       | Software Design Document          | 软件设计文档                         |
| API       | Application Programming Interface | 应用程序编程接口                     |
| RESTful   | Representational State Transfer   | 一种网络应用程序的设计风格和开发方式 |
| B/S       | Browser/Server                    | 浏览器/服务器架构                    |
| Postgres  | Postgresql                        | 一款强大, 可拓展的数据库             |

#### **1.4 参考文献**

1. FastAPI 官方文档
2. SQLModel 官方文档
3. Scrapy 官方文档
4. 课程项目任务说明书

#### **1.5 文档概述**

本文档后续章节的组织结构如下：

- **第2章 体系结构设计**：描述系统的总体架构模式、高层组件及其关系。
- **第3章 详细设计**：深入描述每个模块（API网关、数据持久化、信息获取）的类设计、数据库设计和接口设计。
- **第4章 用户界面设计**：描述前端界面的导航流和关键界面布局。
- **第5章 约束与其他考虑**：说明开发中遇到的技术选型约束、性能要求等。

### **第2章 体系结构设计**

#### **2.1 总体结构**

本系统采用经典的**分层架构**，将系统职责清晰地划分为表现层、应用层和数据层。这种设计确保了关注点分离，提高了模块的内聚性，降低了层与层之间的耦合度，便于开发、测试和维护。

系统的核心数据流由两个独立的进程驱动：

1. **主Web应用进程**：处理用户的交互请求，遵循`前端展示层 -> API网关 -> 数据持久层`的请求/响应流。
2. **数据获取进程**：作为独立的定时任务运行，负责从外部数据源获取数据并更新数据库，遵循`定时任务 -> 爬虫 -> 数据持久层`的数据流。

系统的高层组件图如下所示：

```
+-------------------+      HTTP/RESTful API     +-----------------------+
|                   | <-----------------------> |                       |
|    前端展示层       |                           |       API网关          |
|    (Vue.js)       |                           |      (FastAPI)        |
|                   | ------------------------> |                       |
+-------------------+         JSON Data         +-----------+-----------+
                                                            |
                                                            |  ORM (SQLModel)
                                                            |
                                                +-----------v---------------+
                                                |                           |
                                                |     数据持久层              |
                                                |      (SQLite数据库)        |
                                                |                           |
                                                +-------------+-------------+
                                                              ^
                                                              | ORM/直接操作
                                                              |
                                               +--------------+-------------+
                                               |                            |
                                               |    数据获取系统               |
                                               |    (Scrapy + 定时任务)       |
                                               |                            |
                                               +----------------------------+
显示更多
```

#### **2.2 高层组件描述**

1. **前端展示层**
   - **职责**：为用户提供图形化界面，负责数据的可视化渲染和用户交互。接收用户输入，向API网关发起请求，并将获取到的数据以图表、地图、表格等形式展示。
   - **主要组件**：单页面应用（SPA）、路由管理器、图表组件、地图组件、UI组件库。
   - **对外接口**：通过HTTP协议调用后端RESTful API。
2. **API网关**
   - **职责**：作为系统的核心业务处理单元和唯一入口。接收并验证前端请求，执行相关的业务逻辑，与数据持久层交互进行数据的增删改查操作，并将结果封装为JSON格式返回给前端。
   - **主要组件**：路由处理器、请求验证器、业务逻辑控制器、认证与授权中间件。
   - **对外接口**：提供一组定义良好的RESTful API端点；通过SQLModel ORM与数据库交互。
3. **数据持久层**
   - **职责**：安全、可靠地存储系统的所有持久化数据，包括水利监测数据、工程信息、用户数据等。
   - **主要组件**：SQLite数据库文件、数据库模式（Schemas）。
   - **对外接口**：提供标准的SQL查询接口，通过ORM工具进行访问。
4. **数据获取系统**
   - **职责**：作为一个独立的服务运行，根据预设的调度策略（如每隔一段时间）自动激活。负责从指定的外部数据源（如水利网站）爬取最新数据，经过清洗和转换后，持久化到数据库中。
   - **主要组件**：网络爬虫（Scrapy）、定时任务调度器（如APScheduler）、数据清洗处理器。
   - **对外接口**：通过HTTP请求访问外部数据源；通过数据库接口或ORM写入本地数据库。

#### **2.3 组件间协作**

- **数据查询场景**：用户在前端页面请求历史数据 -> 前端调用`/api/history-data`接口 -> API网关接收到请求，验证用户权限 -> API网关通过ORM查询数据库 -> 数据库返回数据 -> API网关将数据JSON序列化后返回给前端 -> 前端使用ECharts渲染图表。
- **数据更新场景**：定时任务触发器启动 -> 调用Scrapy爬虫程序 -> 爬虫从目标网站抓取数据 -> 数据清洗模块处理数据 -> 将处理后的数据通过ORM写入SQLite数据库。

### **第3章 详细设计**

#### **3.1 数据模型设计**

本节详细定义了系统核心业务逻辑所涉及的主要数据实体、其属性以及实体之间的关系。本系统采用关系型数据库模型，通过外键约束来维护数据的一致性与完整性。

**3.1.1 实体关系描述**
系统的核心实体关系如下图所示，构成了一个清晰的数据结构：

1. **城市与测站 (City - Station)**：一对多关系。一个`城市`可以包含多个`测站`，但一个`测站`必须且只能归属于一个`城市`。
2. **测站与水文数据 (Station - HydrologicalData)**：一对多关系。一个`测站`可以记录多条`水文数据`（包括水位或降雨量），每条`水文数据`必须关联到一个具体的`测站`。
3. **用户 (User)**：`用户`实体相对独立，主要用于系统登录和权限管理，与其他业务实体无直接关联。

**3.1.2 数据字典**
以下表格详细定义了每个实体的字段信息。

**表1：user（用户表）**

| 字段名        | 数据类型     | 约束                       | 描述                        |
| :------------ | :----------- | :------------------------- | :-------------------------- |
| id            | INTEGER      | PRIMARY KEY, AUTOINCREMENT | 用户唯一标识                |
| username      | VARCHAR(50)  | NOT NULL, UNIQUE           | 用户名，用于登录            |
| password_hash | VARCHAR(255) | NOT NULL                   | 加密后的密码                |
| role          | VARCHAR(20)  | NOT NULL                   | 用户角色（如：admin, user） |
| created_at    | DATETIME     | NOT NULL                   | 记录创建时间                |
| updated_at    | DATETIME     | NOT NULL                   | 最后更新时间                |

**表2：city（城市表）**

| 字段名    | 数据类型     | 约束                       | 描述           |
| :-------- | :----------- | :------------------------- | :------------- |
| id        | INTEGER      | PRIMARY KEY, AUTOINCREMENT | 城市唯一标识   |
| name      | VARCHAR(100) | NOT NULL                   | 城市名称       |
| longitude | FLOAT        | NOT NULL                   | 城市中心点经度 |
| latitude  | FLOAT        | NOT NULL                   | 城市中心点纬度 |

**表3：station（测站表）**

| 字段名    | 数据类型     | 约束                                                | 描述         |
| :-------- | :----------- | :-------------------------------------------------- | :----------- |
| id        | INTEGER      | PRIMARY KEY, AUTOINCREMENT                          | 测站唯一标识 |
| name      | VARCHAR(100) | NOT NULL                                            | 测站名称     |
| city_id   | INTEGER      | NOT NULL, FOREIGN KEY (city_id) REFERENCES city(id) | 所属城市ID   |
| longitude | FLOAT        | NOT NULL                                            | 测站精确经度 |
| latitude  | FLOAT        | NOT NULL                                            | 测站精确纬度 |

**表4：hydrological_data（水文数据表）**

| 字段名     | 数据类型    | 约束                                                      | 描述                                            |
| :--------- | :---------- | :-------------------------------------------------------- | :---------------------------------------------- |
| id         | INTEGER     | PRIMARY KEY, AUTOINCREMENT                                | 数据唯一标识                                    |
| station_id | INTEGER     | NOT NULL, FOREIGN KEY (station_id) REFERENCES station(id) | 关联的测站ID                                    |
| type       | VARCHAR(20) | NOT NULL, CHECK (type IN ('WATER_LEVEL', 'RAINFALL'))     | 数据类型：水位 / 降雨量                         |
| value      | FLOAT       | NOT NULL                                                  | 测量值。**单位：水位为米(m)，降雨量为毫米(mm)** |
| measure_at | DATETIME    | NOT NULL                                                  | 数据测量时间点                                  |

------

**本节总结**：以上数据模型清晰地定义了系统的数据结构，支持前端地图展示（依赖经纬度）、历史数据查询（按测站、类型、时间范围）以及用户管理等核心功能。合并后的`hydrological_data`表简化了设计，并能灵活适应不同测站测量不同类型数据的情况。

### **3.2 模块/组件详细设计**

本节将深入系统的主要模块，详细描述其职责、接口和内部逻辑。我们将按照前后端分离的架构，分别对后端API模块、前端Vue.js组件以及SRE/可观测性模块进行设计。

#### **3.2.1 后端API模块设计 (基于FastAPI)**

后端采用基于 **FastAPI** 的现代异步RESTful API风格，利用其自动生成交互式文档、数据验证和依赖注入等特性。以下为核心业务模块的设计。

**1. 用户认证模块 (`auth_router`)**

- **职责**：处理用户登录、令牌验证及权限管理。
- **依赖**：`User` 模型，`get_current_user` 依赖项。
- **接口设计**：
  
  - `POST /api/auth`
    - **描述**：用户登录，获取访问令牌。
    - **请求体**：`Form Data: username, password`
    - **成功响应 (200)**：`{ "access_token": "jwt_token", "token_type": "bearer" }`
  
  - `GET /api/auth/me`
    - **描述**：获取当前登录用户的详细信息。
    - **依赖**：需要有效的Bearer Token。
    - **成功响应 (200)**：`{ "username": "admin", ... }`
  - `POST /api/auth/register`
    - **描述**: 用户注册, 并且获取访问令牌
    - **请求体**: `Register: username, password, role`
    - **成功响应(200)**

**2. 测站管理模块 (`stations_router`)**

- **职责**：提供对测站信息的增删改查（CRUD）接口。
- **依赖**：`Station` Pydantic模型，数据库会话依赖。
- **接口设计**：
  - `GET /api/stations/`
    - **描述**：获取测站列表。支持查询参数过滤（如 `city_id: int`）。
    - **响应模型**：`List[StationRead]`
  - `GET /api/stations/{station_id}`
    - **描述**：获取指定ID的测站详细信息。
    - **响应模型**：`StationRead`
  - `POST /api/stations/` (需管理员权限)
    - **描述**：创建新测站。
    - **请求体模型**：`StationCreate`
  - `PUT /api/stations/{station_id}` (需管理员权限)
  - `DELETE /api/stations/{station_id}` (需管理员权限)

**3. 水文数据模块 (`data_router`)**

- **职责**：处理水位和降雨量数据的查询与录入。
- **依赖**：`WaterLevelData`, `RainfallData` 模型。
- **接口设计**：
  - `GET /api/data/water_level/`
    - **描述**：查询水位数据。支持查询参数：`station_id`（必选），`start_time`, `end_time`。
    - **响应模型**：`List[WaterLevelDataRead]`
  - `GET /api/data/rainfall/`
    - **描述**：查询降雨量数据。参数同上。
    - **响应模型**：`List[RainfallDataRead]`
  - `POST /api/data/batch_upload/` (内部或管理员接口)
    - **描述**：批量导入水文数据。

**4. 数据看板模块 (`dashboard_router`)**

- **职责**：为前端首页看板提供聚合数据。
- **接口设计**：
  - `GET /api/dashboard/summary`
    - **描述**：获取首页摘要信息。
    - **成功响应 (200)**：`{ "total_stations": 50, "latest_data": [ ... ], "alerts": [ ... ] }`
    - **优势**：FastAPI的异步特性使得在此处进行多个数据库查询并聚合结果的性能更高。

#### **3.2.2 前端Vue.js组件设计**

前端采用Vue 3 + Vue Router + Pinia架构。以下是核心路由组件的设计。

**1. 登录视图 (`LoginView.vue`)**

- **职责**：渲染登录表单，处理用户认证。
- **数据**：`username`, `password` (表单数据)。
- **方法**：`handleLogin()` - 调用认证API，成功后保存Token并跳转至首页。
- **路由**：`/login`

**2. 主布局 (`MainLayout.vue`)**

- **职责**：应用的主要布局框架，包含顶部导航栏、侧边栏和主要内容区域 (`<router-view>`)。
- **子组件**：
  - `NavBar.vue`：显示用户信息和登录状态。
  - `SideBar.vue`：提供页面导航菜单。

**3. 数据看板视图 (`DashboardView.vue`)**

- **职责**：系统首页，以地图和图表形式综合展示水文信息。
- **子组件**：
  - `MapContainer.vue`：集成Leaflet地图，根据`Station`的经纬度在地图上标记测站，并展示实时数据。
  - `DataChart.vue`：使用ECharts绘制水位/降雨量的历史趋势折线图。
  - `AlertPanel.vue`：显示超阈值报警信息列表。
- **数据流**：组件挂载后，调用`/api/dashboard/summary`接口获取数据，并分别传递给子组件。地图组件可能单独调用`/api/stations`获取所有测点位置。

**4. 历史数据查询视图 (`HistoryView.vue`)**

- **职责**：提供表单供用户查询特定测站在特定时间段内的历史数据。
- **子组件**：
  - `QueryForm.vue`：包含测站选择器、数据类型选择、时间范围选择器等表单元素。
  - `HistoryChart.vue`：根据查询条件调用对应API (`/api/data/water_level`或`/api/data/rainfall`)，并渲染图表。
- **路由**：`/history`

**5. 系统管理视图 (`AdminView.vue`)**

- **职责**：管理员管理测站和用户（此功能可根据需求决定是否在MVP中实现）。
- **路由**：`/admin`

#### **3.2.3 后端SRE/可观测性模块设计 (基于FastAPI和OpenTelemetry)**

本模块负责收集、导出系统的运行时指标、日志和追踪信息。

**1. 应用初始化与中间件集成 (`main.py`)**

- **职责**：在FastAPI应用启动时，初始化OpenTelemetry并集成必要的中间件。

**2. 指标收集与导出模块 (`metrics.py`)**

- **职责**：创建自定义业务指标，并通过OTLP/gRPC或HTTP协议导出到收集器（如Prometheus）。
- **实现方式**：使用OpenTelemetry Metrics API。

**3. 结构化日志记录**

- **职责**：输出易于解析和查询的结构化日志（JSON格式）。
- **实现方式**：使用`python-json-logger`库，并在日志记录中注入TraceID，实现日志与追踪的关联。

### **3.3 关键算法/逻辑设计**

本节描述系统中核心的业务逻辑和算法实现。

#### **3.3.1 报警阈值检查逻辑**

- **触发时机**：每当系统录入或接收到一条新的水文数据（水位或降雨量）时自动触发。
- **逻辑流程**：
  1. **输入**：新数据点（包含测站ID、数据类型、数值、时间戳）。
  2. **获取阈值**：根据测站ID和数据类型，查询该测站预设的警戒水位或降雨量阈值。阈值可配置在数据库或配置文件中。
  3. **比较判断**：
     - 若 `数据值 > 阈值`，则触发报警。
  4. **报警动作**：
     - **记录**：在`alerts`表或系统事件中创建一条报警记录，状态为“活跃”。
     - **通知**：通过集成消息队列（如Celery）异步发送通知（例如，系统内消息、电子邮件、短信）。
  5. **报警解除**：当后续数据值回落至阈值以下时，将对应报警记录状态更新为“已解除”。

#### **3.3.2 数据聚合查询逻辑（用于图表生成）**

- **触发时机**：前端请求历史数据图表时。
- **问题**：原始数据可能非常密集，直接返回所有数据点会导致前端渲染性能低下和网络传输量大。
- **解决方案**：根据前端请求的时间范围动态决定数据聚合粒度。
  - **时间范围 < 24小时**：返回原始数据或按小时聚合（求平均值）。
  - **时间范围 1天 - 1个月**：按天聚合（求日最大值/平均值）。
  - **时间范围 > 1个月**：按周或月聚合。
- **实现**：此逻辑可在数据库层面通过SQL的`DATE_TRUNC`或`GROUP BY`语句高效完成，避免将所有数据加载到应用层再处理。

#### **3.3.3 用户认证与授权逻辑**

- **密码处理**：
  1. 用户注册或修改密码时，使用如`bcrypt`或`argon2`等安全哈希算法对明文密码进行加盐哈希处理，仅存储哈希值。
  2. 登录时，对输入的密码进行相同的哈希计算，并与存储的哈希值进行安全比较。
- **JWT令牌管理**：
  1. 登录成功后，生成一个JWT，其Payload中包含用户ID、用户名和过期时间。
  2. 后续请求必须在`Authorization`头中携带此令牌。
  3. 保护API时，通过依赖项`get_current_active_user`验证JWT的有效性和签名，并解码出用户信息。

------

### **3.4 接口规范**

本节详细定义系统内部及对外的API接口规范。

#### **3.4.1 公共约定**

- **基础URL**：`https://api.hydrology-system.com/v1`

- **数据格式**：请求与响应体均使用**JSON**格式，除非特殊说明（如文件上传）。

- **HTTP头**：

  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_token>`（需要认证的接口）

- **标准响应结构**：

  ```json
  {
    "status": "success" | "error",
    "data": { ... }, // 成功时返回的数据
    "message": "Descriptive message" // 错误时的错误信息，成功时可为空
  }
  ```

- **错误码**：使用标准HTTP状态码（如200成功，400客户端错误，401未认证，403无权限，404资源不存在，500服务器内部错误）。

#### **3.4.2 核心API接口列表（部分示例）**

**1. 用户认证**

- **接口名称**：获取访问令牌

- **端点**：`POST /auth/token`

- **请求体**：

  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- **成功响应**：

  ```json
  {
    "status": "success",
    "data": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJ...",
      "token_type": "bearer"
    },
    "message": null
  }
  ```

**2. 数据查询**

- **接口名称**：查询水位历史数据

- **端点**：`GET /data/water_level`

- **查询参数**：

  | 参数名        | 类型              | 必选 | 描述                                |
  | :------------ | :---------------- | :--- | :---------------------------------- |
  | `station_id`  | integer           | 是   | 测站ID                              |
  | `start_time`  | string (ISO 8601) | 否   | 开始时间，如 `2023-10-01T00:00:00Z` |
  | `end_time`    | string (ISO 8601) | 否   | 结束时间                            |
  | `aggregation` | string            | 否   | 聚合粒度，如 `hour`, `day`          |

- **成功响应**：

  ```json
  json复制代码{
    "status": "success",
    "data": {
      "station_id": 101,
      "station_name": "长江武汉站",
      "unit": "m",
      "values": [
        {"timestamp": "2023-10-01T01:00:00Z", "value": 12.5},
        {"timestamp": "2023-10-01T02:00:00Z", "value": 12.6}
      ]
    },
    "message": null
  }
  ```

# 第4章 数据库设计

本章详细定义系统的物理数据模型，确保与第3章的模块和接口设计完全对应。本设计基于关系型数据库PostgreSQL。

## 4.1 实体关系设计

系统核心实体包括用户、城市、监测站、水文数据和报警记录。监测站归属于特定城市，水文数据通过监测站采集，报警记录由异常数据触发。这种设计支持城市维度的数据聚合查询和权限管理。

## 4.2 数据表结构设计

### 4.2.1 city（城市表）

存储城市基本信息，支持区域划分和地理信息管理。

| 字段名     | 数据类型                 | 约束             | 默认值            | 描述         |
| :--------- | :----------------------- | :--------------- | :---------------- | :----------- |
| id         | SERIAL                   | PRIMARY KEY      | -                 | 城市唯一标识 |
| name       | VARCHAR(100)             | NOT NULL, UNIQUE | -                 | 城市名称     |
| code       | VARCHAR(20)              | NOT NULL, UNIQUE | -                 | 城市编码     |
| created_at | TIMESTAMP WITH TIME ZONE | -                | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | -                | CURRENT_TIMESTAMP | 记录更新时间 |

索引：idx_city_name (name), idx_city_code(code)

### 4.2.2 station（监测站表）

存储监测站详细信息，包含地理位置和报警阈值设置。

| 字段名              | 数据类型                 | 约束                              | 默认值            | 描述                 |
| :------------------ | :----------------------- | :-------------------------------- | :---------------- | :------------------- |
| id                  | SERIAL                   | PRIMARY KEY                       | -                 | 测站唯一标识         |
| name                | VARCHAR(100)             | NOT NULL                          | -                 | 测站名称             |
| code                | VARCHAR(50)              | NOT NULL, UNIQUE                  | -                 | 测站编码             |
| city_id             | INT                      | FOREIGN KEY REFERENCES cities(id) | -                 | 所属城市ID           |
| latitude            | DECIMAL(10,8)            | NOT NULL                          | -                 | 纬度                 |
| longitude           | DECIMAL(11,8)            | NOT NULL                          | -                 | 经度                 |
| water_level_warning | DECIMAL(8,3)             | -                                 | NULL              | 水位报警阈值(米)     |
| rainfall_warning    | DECIMAL(8,3)             | -                                 | NULL              | 降雨量报警阈值(毫米) |
| is_active           | BOOLEAN                  | NOT NULL                          | true              | 测站是否启用         |
| meta_info           | JSONB                    | -                                 | NULL              | 测站元数据           |
| created_at          | TIMESTAMP WITH TIME ZONE | NOT NULL                          | CURRENT_TIMESTAMP | 记录创建时间         |
| updated_at          | TIMESTAMP WITH TIME ZONE | NOT NULL                          | CURRENT_TIMESTAMP | 记录更新时间         |

索引：idx_station_city_id (city_id), idx_stations_code (code), idx_stations_location (latitude, longitude), idx_station_name(name)

### 4.2.3 water_level_data（水位数据表）

存储水位监测数据，支持时间序列查询和分析。

| 字段名      | 数据类型                 | 约束                                                  | 默认值            | 描述         |
| :---------- | :----------------------- | :---------------------------------------------------- | :---------------- | :----------- |
| id          | SERIAL                   | PRIMARY KEY                                           | -                 | 数据唯一标识 |
| station_id  | INT                      | FOREIGN KEY REFERENCES stations(id) ON DELETE CASCADE | -                 | 关联测站ID   |
| value       | DECIMAL(8,3)             | NOT NULL                                              | -                 | 水位值（米） |
| measure_at  | TIMESTAMP WITH TIME ZONE | NOT NULL                                              | -                 | 测量时间点   |
| data_source | VARCHAR(20)              | NOT NULL                                              | 'auto'            | 数据来源     |
| created_at  | TIMESTAMP WITH TIME ZONE | NOT NULL                                              | CURRENT_TIMESTAMP | 入库时间     |

索引：idx_water_level_composite (station_id, measure_at DESC), idx_water_level_measure_time (measure_at)

### 4.2.4 rainfall_data（降雨量数据表）

存储降雨量监测数据，结构与水位数据表保持一致。

| 字段名     | 数据类型                 | 约束                                                  | 默认值            | 描述             |
| :--------- | :----------------------- | :---------------------------------------------------- | :---------------- | :--------------- |
| id         | SERIAL                   | PRIMARY KEY                                           | -                 | 数据唯一标识     |
| station_id | INT                      | FOREIGN KEY REFERENCES stations(id) ON DELETE CASCADE | -                 | 关联测站ID       |
| value      | DECIMAL(8,3)             | NOT NULL                                              | -                 | 降雨量值（毫米） |
| measure_at | TIMESTAMP WITH TIME ZONE | NOT NULL                                              | -                 | 测量时间点       |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL                                              | CURRENT_TIMESTAMP | 入库时间         |

索引：idx_rainfall_composite (station_id, measure_at DESC), idx_rainfall_measure_time (measure_at)

### 4.2.5 alert（报警记录表）

存储系统生成的报警信息，记录触发条件和处理状态。

| 字段名          | 数据类型                 | 约束                                | 默认值            | 描述                 |
| :-------------- | :----------------------- | :---------------------------------- | :---------------- | :------------------- |
| id              | SERIAL                   | PRIMARY KEY                         | -                 | 报警记录唯一标识     |
| station_id      | INT                      | FOREIGN KEY REFERENCES stations(id) | -                 | 触发报警的测站ID     |
| alert_type      | VARCHAR(20)              | NOT NULL                            | -                 | 报警类型             |
| trigger_value   | DECIMAL(8,3)             | NOT NULL                            | -                 | 触发报警的数据值     |
| threshold_value | DECIMAL(8,3)             | NOT NULL                            | -                 | 报警阈值             |
| trigger_data_id | INT                      | NOT NULL                            | -                 | 触发报警的数据记录ID |
| alert_message   | TEXT                     | -                                   | NULL              | 报警描述信息         |
| status          | VARCHAR(20)              | NOT NULL                            | 'active'          | 报警状态             |
| triggered_at    | TIMESTAMP WITH TIME ZONE | NOT NULL                            | CURRENT_TIMESTAMP | 报警触发时间         |
| resolved_at     | TIMESTAMP WITH TIME ZONE | -                                   | NULL              | 报警解除时间         |
| created_at      | TIMESTAMP WITH TIME ZONE | NOT NULL                            | CURRENT_TIMESTAMP | 记录创建时间         |

索引：idx_alerts_station_status (station_id, status), idx_alerts_triggered_at (triggered_at DESC)

### 4.2.6 user（用户表）

存储系统用户信息，支持角色权限管理。

| 字段名     | 数据类型                 | 约束             | 默认值            | 描述         |
| :--------- | :----------------------- | :--------------- | :---------------- | :----------- |
| id         | SERIAL                   | PRIMARY KEY      | -                 | 用户唯一标识 |
| username   | VARCHAR(50)              | NOT NULL, UNIQUE | -                 | 用户名       |
| email      | VARCHAR(255)             | NOT NULL, UNIQUE | -                 | 邮箱地址     |
| password   | VARCHAR(255)             | NOT NULL         | -                 | 加密密码     |
| role       | VARCHAR(20)              | NOT NULL         | 'user'            | 用户角色     |
| is_active  | BOOLEAN                  | NOT NULL         | true              | 账户是否激活 |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL         | CURRENT_TIMESTAMP | 账户创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL         | CURRENT_TIMESTAMP | 最后更新时间 |

索引：idx_users_username (username), idx_users_email (email), idx_users_role (role)

---

# 第5章 系统实现
## 5.1 技术栈选型
### 5.1.1 后端技术栈

本系统后端采用基于`Python`的现代Web框架`FastAPI`，结合异步编程模式以支持高并发场景。数据库选用功能完善的关系型数据库`PostgreSQL`，通过`SQLAlchemy` ORM进行数据操作。系统采用JWT进行用户认证授权。API文档基于`OpenAPI 3.0`标准自动生成。

### 5.1.2 前端技术栈

前端采用Vue.js 3组合式API架构，使用TypeScript增强代码类型安全。构建工具选用`Vite`

使用`sqlmodel`作为orm

# 第5章 系统实现

## 5.1 技术栈选型

### 5.1.1 后端技术栈

本系统后端采用基于Python的现代Web框架`FastAPI`，结合异步编程模式以支持高并发场景。数据库选用功能完善的关系型数据库`PostgreSQL`，通过`SQLModel` ORM进行数据操作，该ORM结合了`Pydantic`的数据验证能力和`SQLAlchemy`的数据库操作能力。系统采用JWT进行用户认证授权，使用Redis作为缓存和消息队列的存储后端。API文档基于`OpenAPI 3.0`标准自动生成。

### 5.1.2 前端技术栈

前端采用`Vue.js 3`组合式API架构，使用`TypeScript`增强代码类型安全。构建工具选用`Vite`实现快速开发和构建，UI组件库使用Element Plus提供丰富的界面组件。地图可视化基于`Leaflet`实现，图表展示采用`ECharts`库。状态管理使用`Pinia`，路由管理使用`Vue Router`。

### 5.1.3 部署运维技术栈

系统采用`Docker`容器化部署，通过`Docker Compose`编排多服务架构。Web服务器使用`Nginx`作为反向代理和负载均衡器。系统监控使用Prometheus收集指标数据.

## 5.2 核心模块实现

### 5.2.1 数据模型层设计

基于`SQLModel`定义系统核心数据模型，每个模型类同时具备`Pydantic`的数据验证功能和`SQLAlchemy`的数据库映射能力。模型设计采用时间戳混入类，统一管理创建时间和更新时间字段。关系定义通过`SQLModel`的关系功能实现表间关联。

### 5.2.2 API路由层设计

按照功能模块划分路由结构，每个模块对应独立的路由文件。路由层负责请求验证、参数解析和响应格式化。使用`FastAPI`的依赖注入系统管理数据库会话和用户认证状态。API端点采用RESTful设计原则，明确区分不同HTTP方法的语义。

### 5.2.3 服务层设计

服务层封装核心业务逻辑，实现数据处理、业务规则验证和复杂操作流程。服务类之间通过依赖注入实现解耦，每个服务职责单一。数据验证逻辑基于`Pydantic`模型，确保输入输出的数据完整性。

### 5.2.4 数据访问层设计

数据访问层采用Repository模式，封装所有数据库操作细节。通过`SQLModel`的异步会话管理数据库连接，使用异步查询提升系统并发性能。复杂查询通过`SQLModel`的查询构建器实现，简单查询使用CRUD快捷方法。

## 5.3 关键功能实现

### 5.3.1 用户认证授权

实现基于JWT的无状态认证机制，支持用户登录、令牌刷新和权限验证。通过FastAPI的依赖项系统实现路由级别的权限控制。密码采用bcrypt算法进行安全哈希存储，敏感操作记录审计日志。

### 5.3.2 实时数据采集

设计异步数据接收接口，支持批量数据入库。实现数据验证管道，确保采集数据的完整性和准确性。通过`Celery`异步任务处理数据清洗和报警检查，避免阻塞主请求流程。

### 5.3.3 报警规则引擎

实现可配置的阈值报警规则，支持水位和降雨量的多级报警。报警触发采用边缘检测算法，避免重复报警。报警状态机管理报警的生命周期，支持手动确认和自动恢复。

### 5.3.4 数据查询优化

针对时间序列数据特点，实现高效的分页查询和聚合查询。使用数据库索引优化常用查询路径，对大数据量表采用分区策略提升查询性能。查询结果实现多级缓存，减少数据库访问压力。

## 5.4 系统集成实现

### 5.4.1 第三方服务集成

实现与短信网关、邮件服务的集成，支持多通道报警通知。地图服务集成支持多种底图切换和坐标系统转换。外部数据接口实现数据同步和格式转换功能。

### 5.4.2 监控告警集成

系统运行时指标通过`Prometheus`客户端暴露，关键业务指标实现自定义收集。告警规则配置支持阈值告警和异常检测，告警通知实现多级升级策略。

### 5.4.3 日志审计集成

操作日志记录关键业务操作和系统事件，支持操作追踪和安全审计。日志采集实现结构化存储和实时分析，日志查询支持多维度过滤和全文检索。

## 5.5 安全实现

### 5.5.1 数据安全

数据库连接使用SSL加密传输，敏感配置信息通过环境变量管理。用户密码采用加盐哈希存储，API密钥实现定期轮换。数据备份实现自动化流程，支持点-in-time恢复。

### 5.5.2 接口安全

REST API实现速率限制和防重放攻击保护。输入数据实施严格验证和过滤，防止注入攻击。CORS策略配置细粒度的跨域访问控制。

### 5.5.3 运维安全

容器镜像实现漏洞扫描和签名验证。网络策略配置最小权限原则，服务间通信使用双向TLS认证。密钥管理采用专门的密钥管理服务。

本系统通过模块化设计和分层架构，实现了高内聚低耦合的代码结构。采用现代开发工具和最佳实践，确保代码质量和可维护性。基础设施即代码的部署方式保障了环境一致性和快速部署能力。
