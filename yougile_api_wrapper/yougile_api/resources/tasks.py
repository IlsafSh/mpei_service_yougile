"""
Ресурс для работы с задачами.
"""
from typing import Dict, Any, List, Optional
from .base import BaseResource, CRUDResourceMixin


class TasksResource(BaseResource, CRUDResourceMixin):
    """Ресурс для работы с задачами."""
    
    _base_url = '/tasks'
    
    def list(self, board_id: Optional[str] = None, column_id: Optional[str] = None,
             include_deleted: Optional[bool] = None, limit: int = 50, offset: int = 0,
             project_id: Optional[str] = None, title: Optional[str] = None,
             user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить список задач.
        
        Args:
            board_id: ID доски
            column_id: ID колонки
            include_deleted: Включать удаленные задачи
            limit: Количество элементов (по умолчанию 50)
            offset: Индекс первого элемента (по умолчанию 0)
            project_id: ID проекта
            title: Имя задачи
            user_id: ID сотрудника
            
        Returns:
            list: Список задач
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if board_id:
            params['boardId'] = board_id
            
        if column_id:
            params['columnId'] = column_id
            
        if include_deleted is not None:
            params['includeDeleted'] = include_deleted
            
        if project_id:
            params['projectId'] = project_id
            
        if title:
            params['title'] = title
            
        if user_id:
            params['userId'] = user_id
            
        return super().list(**params)
    
    def create(self, title: str, column_id: Optional[str] = None, description: Optional[str] = None,
               archived: Optional[bool] = None, completed: Optional[bool] = None,
               subtasks: Optional[List[str]] = None, assigned: Optional[List[str]] = None,
               deadline: Optional[Dict[str, Any]] = None, timeTracking: Optional[Dict[str, Any]] = None,
               checklists: Optional[List[Dict[str, Any]]] = None, stickers: Optional[Dict[str, Any]] = None,
               color: Optional[str] = None, idTaskCommon: Optional[str] = None, idTaskProject: Optional[str] = None,
               stopwatch: Optional[Dict[str, Any]] = None, timer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Создать задачу.
        
        Args:
            title: Название задачи
            column_id: Id колонки, в которой находится задача
            description: Описание задачи
            archived: Задача перенесена в архив - да/нет
            completed: Задача выполнена - да/нет
            subtasks: Массив Id подзадач
            assigned: Массив Id пользователей, на которых назначена задача
            deadline: Стикер "Дэдлайн". Указывает на крайний срок выполнения задачи
            timeTracking: Стикер "Таймтрекинг". Используется для указания ожидаемого и реального времени на выполнение задачи.
            checklists: Чеклисты. К задаче всегда будет присвоен переданный объект.
            stickers: Стикеры задачи
            color: Цвет карточки задач на доске, доступны цвета: task-primary, task-gray, task-red, task-pink,
            task-yellow, task-green, task-turquoise, task-blue, task-violet
            idTaskCommon: ID задачи, сквозной через всю компанию
            idTaskProject: ID задачи, внутри проекта
            stopwatch: Стикер "Секундомер". Позволяет запустить секундомер, а так же ставить его на паузу и запускать заново.
            timer: Стикер "Таймер". Позволяет установить таймер на заданное время, а также возможность ставить его на паузу и запускать заново
            
        Returns:
            dict: Созданная задача
        """
        data = {
            'title': title
        }
            
        if column_id:
            data['columnId'] = column_id
            
        if description:
            data['description'] = description
            
        if archived:
            data['archived'] = archived
            
        if completed is not None:
            data['completed'] = completed
            
        if subtasks is not None:
            data['subtasks'] = subtasks
            
        if assigned:
            data['assigned'] = assigned
            
        if deadline is not None:
            data['deadline'] = deadline
            
        if timeTracking:
            data['timeTracking'] = timeTracking

        if checklists:
            data['checklists'] = checklists
            
        if stickers:
            data['stickers'] = stickers
            
        if color:
            data['color'] = color

        if idTaskCommon:
            data['idTaskCommon'] = idTaskCommon

        if idTaskProject:
            data['idTaskProject'] = idTaskProject

        if stopwatch:
            data['stopwatch'] = stopwatch

        if timer:
            data['timer'] = timer
            
        return super().create(**data)
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Получить задачу по ID.
        
        Args:
            id: ID задачи
            
        Returns:
            dict: Задача
        """
        return super().get(id)
    
    def update(self, id: str, deleted: Optional[bool] = None, title: Optional[str] = None,
               column_id: Optional[str] = None, description: Optional[str] = None, archived: Optional[bool] = None,
               completed: Optional[bool] = None, subtasks: Optional[List[str]] = None,
               assigned: Optional[List[str]] = None, deadline: Optional[Dict[str, Any]] = None,
               timeTracking: Optional[Dict[str, Any]] = None, checklists: Optional[List[Dict[str, Any]]] = None,
               stickers: Optional[Dict[str, Any]] = None, color: Optional[str] = None,
               idTaskCommon: Optional[str] = None, idTaskProject: Optional[str] = None,
               stopwatch: Optional[Dict[str, Any]] = None, timer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обновить задачу.
        
        Args:
            id: ID задачи
            deleted: Если true, значит объект удален
            title: Название задачи
            column_id: Id колонки, в которой находится задача
            description: Описание задачи
            archived: Задача перенесена в архив - да/нет
            completed: Задача выполнена - да/нет
            subtasks: Массив Id подзадач
            assigned: Массив Id пользователей, на которых назначена задача
            deadline: Стикер "Дэдлайн". Указывает на крайний срок выполнения задачи
            timeTracking: Стикер "Таймтрекинг". Используется для указания ожидаемого и реального времени на выполнение задачи.
            checklists: Чеклисты. К задаче всегда будет присвоен переданный объект.
            stickers: Стикеры задачи
            color: Цвет карточки задач на доске, доступны цвета: task-primary, task-gray, task-red, task-pink,
            task-yellow, task-green, task-turquoise, task-blue, task-violet
            idTaskCommon: ID задачи, сквозной через всю компанию
            idTaskProject: ID задачи, внутри проекта
            stopwatch: Стикер "Секундомер". Позволяет запустить секундомер, а так же ставить его на паузу и запускать заново.
            timer: Стикер "Таймер". Позволяет установить таймер на заданное время, а также возможность ставить его на паузу и запускать заново
            
        Returns:
            dict: Обновленная задача
        """
        data = {}

        if deleted:
            data['deleted'] = deleted

        if title:
            data['title'] = title

        if column_id:
            data['columnId'] = column_id

        if description:
            data['description'] = description

        if archived:
            data['archived'] = archived

        if completed is not None:
            data['completed'] = completed

        if subtasks is not None:
            data['subtasks'] = subtasks

        if assigned:
            data['assigned'] = assigned

        if deadline is not None:
            data['deadline'] = deadline

        if timeTracking:
            data['timeTracking'] = timeTracking

        if checklists:
            data['checklists'] = checklists

        if stickers:
            data['stickers'] = stickers

        if color:
            data['color'] = color

        if idTaskCommon:
            data['idTaskCommon'] = idTaskCommon

        if idTaskProject:
            data['idTaskProject'] = idTaskProject

        if stopwatch:
            data['stopwatch'] = stopwatch

        if timer:
            data['timer'] = timer
            
        return super().update(id, **data)
