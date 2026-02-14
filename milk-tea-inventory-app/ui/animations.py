"""
BrewMetric Animations Module
UI animations, transitions, and threading utilities.
"""

import threading
from typing import Callable
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QRect, QPoint, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from config import ANIMATION_DURATION_FAST, ANIMATION_DURATION_NORMAL, ANIMATION_DURATION_SLOW


class AnimationManager:
    """Manager for UI animations and effects."""
    
    @staticmethod
    def fade_in_widget(widget: QWidget, duration: int = ANIMATION_DURATION_NORMAL):
        """
        Fade in a widget by increasing opacity.
        
        Args:
            widget: Widget to fade in
            duration: Animation duration in milliseconds
        """
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation
    
    @staticmethod
    def fade_out_widget(widget: QWidget, duration: int = ANIMATION_DURATION_NORMAL):
        """
        Fade out a widget by decreasing opacity.
        
        Args:
            widget: Widget to fade out
            duration: Animation duration in milliseconds
        """
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation
    
    @staticmethod
    def move_widget(
        widget: QWidget,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        duration: int = ANIMATION_DURATION_NORMAL
    ):
        """
        Slide widget from start to end position.
        
        Args:
            widget: Widget to move
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            duration: Animation duration in milliseconds
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(QPoint(*start_pos))
        animation.setEndValue(QPoint(*end_pos))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation
    
    @staticmethod
    def resize_widget(
        widget: QWidget,
        start_size: tuple[int, int],
        end_size: tuple[int, int],
        duration: int = ANIMATION_DURATION_NORMAL
    ):
        """
        Resize widget with animation.
        
        Args:
            widget: Widget to resize
            start_size: Starting size (width, height)
            end_size: Ending size (width, height)
            duration: Animation duration in milliseconds
        """
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(QSize(*start_size))
        animation.setEndValue(QSize(*end_size))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation
    
    @staticmethod
    def color_transition(
        widget: QWidget,
        start_color: str,
        end_color: str,
        duration: int = ANIMATION_DURATION_NORMAL,
        property_name: str = "palette"
    ):
        """
        Transition widget color.
        
        Args:
            widget: Widget to animate
            start_color: Starting color (hex)
            end_color: Ending color (hex)
            duration: Animation duration in milliseconds
            property_name: Property to animate
        """
        animation = QPropertyAnimation(widget, property_name.encode())
        animation.setDuration(duration)
        animation.setStartValue(QColor(start_color))
        animation.setEndValue(QColor(end_color))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation
    
    @staticmethod
    def pulse_widget(
        widget: QWidget,
        start_size: tuple[int, int],
        pulse_size: tuple[int, int],
        cycles: int = 2,
        duration: int = ANIMATION_DURATION_NORMAL
    ):
        """
        Create a pulsing effect on a widget.
        
        Args:
            widget: Widget to pulse
            start_size: Normal size
            pulse_size: Pulsed size
            cycles: Number of pulse cycles
            duration: Total animation duration
        """
        # This would need multiple animations chained together
        # Simplified version - single pulse
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration // 2)
        animation.setStartValue(QSize(*start_size))
        animation.setEndValue(QSize(*pulse_size))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation


class LoadingSpinner:
    """Custom loading spinner widget."""
    
    def __init__(self, parent: QWidget = None):
        """Initialize spinner."""
        self.parent = parent
        self.angle = 0
        self.is_spinning = False
    
    def start(self):
        """Start spinning animation."""
        self.is_spinning = True
        self._animate()
    
    def stop(self):
        """Stop spinning animation."""
        self.is_spinning = False
    
    def _animate(self):
        """Animate the spinner."""
        if self.is_spinning:
            self.angle = (self.angle + 30) % 360
            # Update spinner visual here
            threading.Timer(0.05, self._animate).start()


class ThreadManager:
    """Manager for background thread operations."""
    
    @staticmethod
    def run_in_thread(
        func: Callable,
        *args,
        on_complete: Callable = None,
        on_error: Callable = None,
        **kwargs
    ) -> threading.Thread:
        """
        Run a function in a background thread.
        
        Args:
            func: Function to run
            args: Positional arguments for function
            on_complete: Callback function when complete (receives return value)
            on_error: Callback function on error (receives exception)
            kwargs: Keyword arguments for function
            
        Returns:
            Thread object
        """
        def thread_worker():
            try:
                result = func(*args, **kwargs)
                if on_complete:
                    on_complete(result)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    print(f"[v0] Thread error: {e}")
        
        thread = threading.Thread(target=thread_worker, daemon=True)
        thread.start()
        return thread
    
    @staticmethod
    def run_with_timeout(
        func: Callable,
        timeout: float,
        *args,
        **kwargs
    ) -> tuple[bool, any]:
        """
        Run a function with timeout.
        
        Args:
            func: Function to run
            timeout: Timeout in seconds
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Tuple of (success, result)
        """
        result = [None]
        exception = [None]
        
        def thread_worker():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=thread_worker, daemon=True)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            return False, "Operation timed out"
        
        if exception[0]:
            return False, str(exception[0])
        
        return True, result[0]


class PageTransition:
    """Manages transitions between pages/views."""
    
    @staticmethod
    def transition_to_page(
        from_widget: QWidget,
        to_widget: QWidget,
        duration: int = ANIMATION_DURATION_NORMAL
    ):
        """
        Transition from one page to another.
        
        Args:
            from_widget: Current page widget
            to_widget: Target page widget
            duration: Transition duration in milliseconds
        """
        # Fade out current page
        AnimationManager.fade_out_widget(from_widget, duration // 2)
        
        # After fade out, hide current and show new
        def on_fade_complete():
            from_widget.hide()
            to_widget.show()
            AnimationManager.fade_in_widget(to_widget, duration // 2)
        
        # For simple implementation, we'll use a basic transition
        from_widget.hide()
        to_widget.show()
        AnimationManager.fade_in_widget(to_widget, duration)


class ProgressBar:
    """Custom progress bar with animation."""
    
    def __init__(self, parent: QWidget = None):
        """Initialize progress bar."""
        self.parent = parent
        self.current_value = 0
        self.max_value = 100
    
    def set_value(self, value: int):
        """
        Set progress value with animation.
        
        Args:
            value: Value to set (0-100)
        """
        self.current_value = min(value, self.max_value)
    
    def reset(self):
        """Reset progress to 0."""
        self.current_value = 0
    
    def increment(self, amount: int = 10):
        """
        Increment progress value.
        
        Args:
            amount: Amount to increment
        """
        self.set_value(self.current_value + amount)
