"""Simple tests for OpenTelemetry configuration and instrumentation."""

import logging
import os
import sys
from unittest import mock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from opentelemetry import trace

from skill_sphere_mcp.telemetry.otel import setup_telemetry


class TestSetupTelemetrySimple:
    """Test OpenTelemetry setup functionality."""

    @pytest.fixture(autouse=True)
    def setup_logging(self) -> None:
        """Setup logging for tests."""
        logging.basicConfig(level=logging.DEBUG)

    @mock.patch("skill_sphere_mcp.telemetry.otel.get_settings")
    @mock.patch("skill_sphere_mcp.telemetry.otel.Resource")
    @mock.patch("skill_sphere_mcp.telemetry.otel.TracerProvider")
    @mock.patch("skill_sphere_mcp.telemetry.otel.OTLPSpanExporter")
    @mock.patch("skill_sphere_mcp.telemetry.otel.BatchSpanProcessor")
    @mock.patch("skill_sphere_mcp.telemetry.otel.trace")
    def test_setup_telemetry_success(
        self,
        mocks,
    ) -> None:
        (
            mock_trace,
            mock_batch_processor,
            mock_exporter,
            mock_provider,
            mock_resource,
            mock_get_settings,
        ) = mocks
        """Test successful telemetry setup."""
        # Mock settings
        mock_settings = mock.MagicMock()
        mock_settings.otel_service_name = "test-service"
        mock_settings.otel_endpoint = "http://localhost:4317"
        mock_get_settings.return_value = mock_settings

        # Mock OpenTelemetry components
        mock_resource_instance = mock.MagicMock()
        mock_resource.create.return_value = mock_resource_instance

        mock_provider_instance = mock.MagicMock()
        mock_provider.return_value = mock_provider_instance

        mock_exporter_instance = mock.MagicMock()
        mock_exporter.return_value = mock_exporter_instance

        mock_processor_instance = mock.MagicMock()
        mock_batch_processor.return_value = mock_processor_instance

        mock_tracer = mock.MagicMock()
        mock_trace.get_tracer.return_value = mock_tracer

        # Call the function
        result = setup_telemetry()

        # Verify all components were created correctly
        mock_resource.create.assert_called_once_with({"service.name": "test-service"})
        mock_provider.assert_called_once_with(resource=mock_resource_instance)
        mock_exporter.assert_called_once_with(endpoint="http://localhost:4317")
        mock_batch_processor.assert_called_once_with(mock_exporter_instance)
        mock_provider_instance.add_span_processor.assert_called_once_with(
            mock_processor_instance
        )
        mock_trace.set_tracer_provider.assert_called_once_with(mock_provider_instance)
        mock_trace.get_tracer.assert_called_once_with("skill_sphere_mcp.telemetry.otel")

        # Verify the function returns the tracer
        assert result == mock_tracer

    @mock.patch("skill_sphere_mcp.telemetry.otel.get_settings")
    @mock.patch("skill_sphere_mcp.telemetry.otel.logger")
    def test_setup_telemetry_settings_error(
        self, mock_logger, mock_get_settings
    ) -> None:
        """Test telemetry setup when settings raise an error."""
        # Mock settings to raise an error
        mock_get_settings.side_effect = ValueError("Invalid settings")

        # Call the function
        result = setup_telemetry()

        # Verify error was logged
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert call_args[0][0] == "Failed to setup OpenTelemetry: %s"
        assert isinstance(call_args[0][1], ValueError)
        assert str(call_args[0][1]) == "Invalid settings"

        # Verify function returns None on error
        assert result is None

    @mock.patch("skill_sphere_mcp.telemetry.otel.get_settings")
    @mock.patch("skill_sphere_mcp.telemetry.otel.Resource")
    @mock.patch("skill_sphere_mcp.telemetry.otel.logger")
    def test_setup_telemetry_resource_error(
        self, mock_logger, mock_resource, mock_get_settings
    ) -> None:
        """Test telemetry setup when Resource creation fails."""
        # Mock settings
        mock_settings = mock.MagicMock()
        mock_settings.otel_service_name = "test-service"
        mock_settings.otel_endpoint = "http://localhost:4317"
        mock_get_settings.return_value = mock_settings

        # Mock Resource to raise an error
        mock_resource.create.side_effect = RuntimeError("Resource creation failed")

        # Call the function
        result = setup_telemetry()

        # Verify error was logged
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert call_args[0][0] == "Failed to setup OpenTelemetry: %s"
        assert isinstance(call_args[0][1], RuntimeError)
        assert str(call_args[0][1]) == "Resource creation failed"

        # Verify function returns None on error
        assert result is None

    def test_setup_telemetry_integration(self) -> None:
        """Test telemetry setup with minimal mocking to verify integration."""
        with mock.patch(
            "skill_sphere_mcp.telemetry.otel.get_settings"
        ) as mock_get_settings:
            # Mock settings
            mock_settings = mock.MagicMock()
            mock_settings.otel_service_name = "test-service"
            mock_settings.otel_endpoint = "http://localhost:4317"
            mock_get_settings.return_value = mock_settings

            # Call the function
            result = setup_telemetry()

            # Verify we get a tracer back
            assert result is not None
            assert isinstance(result, trace.Tracer)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
