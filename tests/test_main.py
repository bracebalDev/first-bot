from unittest.mock import patch

from first_bot.main import main


def test_main_executes_orchestrator():
    with patch("first_bot.main.Orchestrator") as mock_orch_cls:
        mock_instance = mock_orch_cls.return_value
        main()
        mock_orch_cls.assert_called_once()
        mock_instance.run.assert_called_once()
