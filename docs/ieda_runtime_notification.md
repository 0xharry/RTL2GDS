# Analysis on how sending runtime messages works

Let's create a scenario and analysis step by step:

## 1. RTL2GDS `cloud_app` @design_zoo/cloud_app/cloud.py received a `routing` request:

- Endpoint: `eda_service_host:eda_service_port/apis/v1/ieda/stdin`

- Request paylod:

```json
{
    "projectId": "42",
    "taskId": "7",
    "taskType": "routing",
    "parameter": {
        "fast_route": "false"
    }
}
```

---

## 2. The `cloud_app` generate necessary paths and files, and calls `rtl2gds.cloud_main`

- Paths

```python
proj_workspace = MOUNT_POINT / f"project_{project_id}" # probably `/projectData/project_42`
task_workspace = proj_workspace / f"task_{task_id}"    # probably `/projectData/project_42/task_7`
config_yaml = proj_workspace / "config.yaml"           # probably `/projectData/project_42/config.yaml`
```

- Files: `config.yaml`

```yaml
FAST_ROUTE: false
RESULT_DIR: /projectData/project_42/task_7  # task_workspace
RTL_FILE: /projectData/project_42/top.v  # a temp fixed name
```

- **@TODO 1**: PASS these parameters to step `env` in `step_template.py`

```yaml
IEDA_ECOS_NOTIFICATION_URL: ${HOST}:${PORT}/apis/v1/ieda/running_notify
IEDA_ECOS_NOTIFICATION_SECRET: ${SECRET}
ECOS_TASK_ID: task_id # 7
ECOS_PROJECT_ID: project_id # 42
ECOS_TASK_TYPE: ${STEP_NAME}
```

- Calls `rtl2gds.cloud_main` with arguments `step_name` and `config_yaml`

---

## 3. Create `Chip` instance and run `cloud_step`

- Initialize `Chip` with `config_yaml`

- **@TODO 2**: ADD `step_parameters` to chip as a context management feature

```python
class Chip:
    def __init__(
        self,
        chip.step_parameters: dict[str: dict{}] = {
            "step_name": {
                "env_key": "env_value",
            },
            "routing": {
                "FAST_ROUTE": "false",
                "RESULT_DIR": "/projectData/project_42/task_7",
                "RTL_FILE": "/projectData/project_42/top.v"
            }
        }
    )
```

- Run each `cloud_step` by `StepWrapper`

- Update `step_parameters` with `chip.step_parameters[step_name]` before calls actual `Step.run()`

---

### 4. Calls `Step.run()` and run

- The pre mentioned `step_parameters` are now `parameters` used to resolve step templates and as subprocess enviroument variables

- Start a subprocess to run iEDA at `Step._run_shell()`

the final command would be:

```python
shell_cmd = [
    "iEDA",
    "${R2G_TOOL_DIR}/iEDA/script/iRT_script/run_iRT.tcl"
]
merged_env = {
    **Step.r2g_template_value,
    **parameters, # Chip.step_parameters are now ENV var
    **input_files,
    **input_parameters,
    **output_files,
}
```

### 5. initialize ieda::NotificationUtility and send notification at each iRT iteration

- initialize `ieda::NotificationUtility` with:

```cpp
// std::string NotificationUtility::loadAuthTokenFromEnv():
const char* token          = std::getenv("IEDA_ECOS_NOTIFICATION_SECRET");
// bool NotificationUtility::initialize(const std::string& endpoint_url):
const char* env_url        = std::getenv("IEDA_ECOS_NOTIFICATION_URL");
const char* env_task_id    = std::getenv("ECOS_TASK_ID");
const char* env_project_id = std::getenv("ECOS_PROJECT_ID");
const char* env_task_type  = std::getenv("ECOS_TASK_TYPE");
```

- send notification using `sendNotification` and calls `performHttpRequest` for the http request:

```cpp
NotificationUtility::HttpResponse NotificationUtility::sendNotification(
    const std::string& tool_name, 
    const std::map<std::string, std::string>& metadata
)
NotificationUtility::HttpResponse NotificationUtility::performHttpRequest(
    const std::string& payload_json
)
curl_easy_perform(curl)
```

---

### 6. RTL2GDS `cloud_app` listens `/apis/v1/ieda/running_notify` and receives the notification

### 7. 
