ENV_LOCATION?=virtualenv
ENV_ACTIVATE=environment

help:
	@echo "Faceoff Makefile"
	@echo "\nOptions\n"
	@echo "  ENV_LOCATION (Default: $(ENV_LOCATION))"
	@echo "  ENV_ACTIVATE (Default: $(ENV_ACTIVATE))"
	@echo "\nTargets\n"
	@echo "  $(ENV_ACTIVATE) - Create virtual project environment."
	@echo "  clean - Remove generated build files."
	@echo "  help - Show this help text."

$(ENV_ACTIVATE):
	$(call installed,python)
	$(call installed,virtualenv)
	make clean
	virtualenv --prompt='(faceoff) ' $(ENV_LOCATION)
	rm -f $(ENV_ACTIVATE)
	ln -s $(ENV_LOCATION)/bin/activate $(ENV_ACTIVATE)
	source $(ENV_ACTIVATE); pip install -q -r requirements.txt

clean:
	rm -rf $(ENV_LOCATION)
	rm -f $(ENV_ACTIVATE)

installed = \
	@(which $(1) > /dev/null) || (echo "error: $(1) not installed" && exit 1)

.PHONY: clean help
