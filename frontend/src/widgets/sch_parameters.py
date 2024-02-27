import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple

from features.task_validator import (  # Assuming custom import, details unknown
    get_task_enum_name,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from widgets.ui_factory import (  # Assuming custom import, details unknown
    UIComponentFactory,
)


class ParameterConfiguration(QWidget):
    """
    A class to dynamically configure and display UI components based on task parameters.

    Attributes:
        task_dictionary (Dict[str, Dict[str, Callable]]): A mapping of device names to tasks,
            where each task is represented by a function defining its parameters.
        task_enum (Optional[Any]): An optional enumeration to categorize tasks. The exact type
            is not specified, allowing for flexibility in task categorization.
        widget_cache (Dict[Tuple[str, str], QWidget]): A cache to store generated UI components
            for quick retrieval, avoiding redundant UI construction.
        stacked_widget (QStackedWidget): A widget that can stack multiple child widgets, showing one at a time.
        main_layout (QVBoxLayout): The main layout for arranging child widgets vertically.
    """

    def __init__(
        self,
        task_dictionary: Dict[str, Dict[str, Callable]],
        parent: Optional[QWidget] = None,
        task_enum: Optional[Any] = None,
    ) -> None:
        super().__init__(parent)
        self.task_dictionary: Dict[str, Dict[str, Callable]] = task_dictionary
        self.task_enum: Optional[Any] = task_enum
        self.widget_cache: Dict[Tuple[str, str], QWidget] = {}
        self.stacked_widget: QStackedWidget = QStackedWidget(self)
        self.main_layout: QVBoxLayout = QVBoxLayout(self)
        self.main_layout.addWidget(self.stacked_widget)
        self.setLayout(self.main_layout)

    def updateUI(self, device: str, task_name: str) -> None:
        """
        Updates the UI to display the configuration for the specified device and task.

        Args:
            device (str): The name of the device for which the UI should be updated.
            task_name (str): The name of the task for which the UI should be updated.
        """
        cache_key: Tuple[str, str] = (device, task_name)
        if cache_key not in self.widget_cache:
            task_func: Optional[Callable] = self.task_dictionary.get(device, {}).get(
                task_name
            )
            spec: List[QWidget] = self._infer_ui_spec_from_function(task_func)
            container_widget: QWidget = self.generateUI(spec)
            self.widget_cache[cache_key] = container_widget
            self.stacked_widget.addWidget(container_widget)

        index: int = self.stacked_widget.indexOf(self.widget_cache[cache_key])
        self.stacked_widget.setCurrentIndex(index)

    def _infer_ui_spec_from_function(self, func: Callable) -> List[QWidget]:
        """
        Infers the UI specification from a function's parameters to generate appropriate widgets.

        Args:
            func (Callable): The function from which to infer UI components.

        Returns:
            List[QWidget]: A list of widgets that correspond to the function's parameters.
        """
        spec: List[QWidget] = []
        sig: inspect.Signature = inspect.signature(func)
        param_types: Dict[str, Any] = {
            name: param.annotation
            for name, param in sig.parameters.items()
            if param.default is inspect.Parameter.empty
        }
        param_constraints: Dict[str, Any] = getattr(func, "param_constraints", {})
        for param, expected_type in param_types.items():
            constraints: Optional[Dict[str, Any]] = param_constraints.get(param)
            widget_spec: QWidget = UIComponentFactory.create_widget(
                param, None, expected_type, constraints
            )
            spec.append(widget_spec)
        return spec

    def generateUI(self, spec: List[QWidget]) -> QWidget:
        """
        Generates a UI container with widgets based on the provided specification.

        Args:
            spec (List[QWidget]): A list of widget specifications to include in the UI.

        Returns:
            QWidget: A container widget with the specified UI components.
        """
        container: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(container)
        for widget in spec:
            layout.addWidget(widget)
        container.setLayout(layout)
        return container

    def getUserData(self, task_spec: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Retrieves user input data from the current UI configuration.

        Args:
            task_spec (List[Dict[str, Any]]): A specification of the task for which to collect input data.

        Returns:
            Dict[str, Any]: A dictionary containing the collected input data.
        """
        parameters: Dict[str, Any] = {}
        current_container: Optional[QWidget] = self.stacked_widget.currentWidget()
        if not current_container:
            return parameters

        for spec in task_spec:
            kwarg_label: str = spec.get("kwarg_label", spec.get("label"))
            layout: QVBoxLayout = current_container.layout()
            for i in range(layout.count()):
                layout_item = layout.itemAt(i)
                widget: QWidget = layout_item.widget()
                if isinstance(widget, QLabel) and widget.text() == spec["label"]:
                    input_widget: Optional[QWidget] = (
                        layout.itemAt(i + 1).widget()
                        if i + 1 < layout.count()
                        else None
                    )
                    if input_widget:
                        value: Any = UIComponentFactory.extract_value(input_widget)
                        if value is not None:
                            parameters[kwarg_label] = value
                    break

        return parameters

    def getConfiguration(self, device, task_name):
        """
        Collects the validated configuration from the UI and prepares it for use or saving.

        Args:

        Returns:
            Dict[str, Any]: A dictionary containing the validated configuration.
        """
        current_container = (
            self.stacked_widget.currentWidget()
        )  # Get the visible container
        if not current_container:
            return {}  # Return empty dict if no container is visible

        parameters = {}
        task_spec = self._infer_ui_spec_from_function(
            self.task_dictionary.get(device, {}).get(task_name)
        )

        for spec in task_spec:
            kwarg_label = spec.get("kwarg_label", spec.get("label"))
            layout = current_container.layout()
            for i in range(layout.count()):
                layout_item = layout.itemAt(i)
                widget = layout_item.widget()
                if isinstance(widget, QLabel) and widget.text() == spec["label"]:
                    input_widget = (
                        layout.itemAt(i + 1).widget()
                        if i + 1 < layout.count()
                        else None
                    )
                    if input_widget:
                        value = UIComponentFactory.extract_value(input_widget)
                        if value is not None:  # Only add if extraction was successful
                            parameters[kwarg_label] = value
                    break  # Break after finding the widget to avoid unnecessary iterations

        return parameters
