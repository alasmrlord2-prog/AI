# Unified Permission System - نظام الصلاحيات الموحد

## نظرة عامة

تم إنشاء نظام صلاحيات موحد يتحكم بكل الواجهات والميزات في النظام. النظام يعمل على أساس:

1. **Agent Modes**: Safe, DevOps, Root, Short
2. **Memory Modes**: Off, Short, Long
3. **Tool Permissions**: التحكم بالأدوات الفردية
4. **Feature Permissions**: التحكم بالميزات الكاملة

## Agent Modes

### Safe Mode
- يسمح فقط بـ: `read_file`, `doc_search`, `read_logs`
- ممنوع تماماً: `run_shell`, `write_file`, `restart_service`
- أي محاولة خارجة عن الأدوات المسموح بها تتوقف برسالة Denied

### DevOps Mode
- يسمح بكل الأدوات
- لكن `run_shell`, `write_file`, `restart_service`, `backup.restore`, `cicd.deploy` تحتاج موافقة (approval)
- رفض التنفيذ يرجّع error للAgent

### Root Mode
- كل الأدوات مسموحة
- بدون أي approval
- agent-core يقدر ينفذ أوامر مباشرة

### Short Mode
- agent-memory ما يخزّن شي نهائي
- كل السياق يختفي بعد انتهاء المحادثة/الجلسة

## Memory Modes

### Off
- memory.json و long_memory.json يتم تعطيلهم
- أي محاولة write_memory تنرفض

### Short
- البيانات تروح فقط للذاكرة المؤقتة داخل الجلسة
- ما تتخزن على disk
- reset عند كل refresh

### Long
- تفعيل memory.json
- إذا موجود DB، استخدم DB للlong-term memory
- الAgent يسترجع السياق القديم تلقائيًا بكل session

## Tool Permissions

الإعدادات التالية تتحكم مباشرة بأدوات الـ Agent:

- `allow_shell`: يتحكم بـ `run_shell`
- `allow_read_file`: يتحكم بـ `read_file`
- `allow_doc_search`: يتحكم بـ `doc_search`
- `allow_logs`: يتحكم بـ `read_logs`

## Feature Permissions

كل ميزة في النظام لها permission key خاص:

| Feature | Permission Key | Tools Required |
|---------|---------------|----------------|
| Security Scan | `security.scan` | read_file, run_shell |
| Repository Scan | `security.repo_scan` | read_file |
| CI/CD Deploy | `cicd.deploy` | run_shell |
| AI Debugger | `debugger.analyze` | read_logs |
| Backup Create | `backup.create` | run_shell |
| Backup Restore | `backup.restore` | run_shell |
| Workflow Execute | `workflow.execute` | run_shell |

## API Usage

### التحقق من الصلاحية

```python
from app.core.permission_helpers import check_action_permission

# في API endpoint
@router.post("/my-endpoint")
async def my_endpoint(current_user: dict = Depends(get_current_user)):
    check_action_permission("security.scan", current_user, resource="/path/to/resource")
    # إذا الصلاحية مرفوضة، سيتم رفع HTTPException تلقائياً
    # إذا تحتاج approval، سيتم إنشاء pending action تلقائياً
```

### التحقق من Tool

```python
from app.core.permission_helpers import check_tool_permission

@router.post("/run-command")
async def run_command(current_user: dict = Depends(get_current_user)):
    check_tool_permission("run_shell", current_user)
    # تنفيذ الأمر...
```

### API Endpoints

#### GET /api/permissions/validate?action=security.scan
التحقق من صلاحية action معينة

#### POST /api/permissions/validate
```json
{
  "action": "security.scan",
  "tool_name": "run_shell",
  "resource": "/path/to/resource",
  "server": "aws-prod"
}
```

#### GET /api/permissions/list
قائمة بكل الصلاحيات وحالتها

#### GET /api/permissions/actions
قائمة بكل Actions المسموحة

#### GET /api/permissions/actions/requiring-approval
قائمة بكل Actions التي تحتاج موافقة

#### GET /api/permissions/feature/{feature_name}
معلومات عن صلاحية ميزة معينة

## Approval System

عندما يكون action يحتاج موافقة:

1. يتم إنشاء pending action تلقائياً
2. يتم إرجاع `action_id` في الـ response
3. Admin/DevOps يمكنهم الموافقة أو الرفض من `/api/pending-actions`
4. بعد الموافقة، يتم تنفيذ الـ action تلقائياً

## Multi-Server Support (قيد التطوير)

النظام يدعم إضافة servers متعددة في Settings:

```json
{
  "servers": [
    {
      "name": "aws-prod",
      "host": "18.x.x.x",
      "port": 9090,
      "protocol": "ws",
      "token": "secret-token",
      "enabled": true
    }
  ],
  "default_server": "local"
}
```

عند تنفيذ action، يمكن تحديد server:

```json
{
  "action": "read_file",
  "path": "/etc/nginx/nginx.conf",
  "server": "aws-prod"
}
```

## Integration في الواجهات

كل واجهة في Dashboard يجب أن تستخدم Permission Engine قبل تنفيذ أي إجراء:

```typescript
// Frontend example
const checkPermission = async (action: string) => {
  const response = await fetch(`/api/permissions/validate?action=${action}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const result = await response.json();
  
  if (!result.allowed) {
    alert(result.reason);
    return false;
  }
  
  if (result.requires_approval) {
    // Show approval dialog
    const approved = await showApprovalDialog(result.action_id);
    if (!approved) return false;
  }
  
  return true;
};
```

## Security Notes

⚠️ **مهم جداً**:
- Root mode يعطي صلاحيات كاملة - استخدمه بحذر
- كل Node Agent يجب أن يكون محمي بـ token قوي
- WebSocket connections يجب أن تكون مؤمنة بـ SSL
- Tokens يجب أن تكون rotated بانتظام
- السيرفرات يجب أن تكون مراقبة

## Examples

### Example 1: Security Scan
```python
# API endpoint
@router.post("/security/scan")
async def scan(current_user: dict = Depends(get_current_user)):
    check_action_permission("security.scan", current_user)
    # Safe to execute scan...
```

### Example 2: CI/CD Deploy
```python
@router.post("/cicd/deploy")
async def deploy(current_user: dict = Depends(get_current_user)):
    check_action_permission("cicd.deploy", current_user, resource="production")
    # If DevOps mode, will require approval
    # If Root mode, executes immediately
```

### Example 3: Tool Usage
```python
@router.post("/tools/run-shell")
async def run_shell(cmd: str, current_user: dict = Depends(get_current_user)):
    check_tool_permission("run_shell", current_user)
    # Execute command...
```

