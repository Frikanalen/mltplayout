install:
	adduser --system --no-create-home --shell /bin/nologin fk-playout
	mkdir -p /var/log/fk-playout
	install -m 644 etc/fk-playout.service /etc/systemd/system/
	    systemctl daemon-reload
