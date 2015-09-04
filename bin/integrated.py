import os, sys
import datetime
import logging
from logging import handlers

from vision import playout, playlist, playoutweb, pgsched, clock
from vision.configuration import configuration

def sanity_test():
	# TODO: Create a proper sanity test
	if not os.path.isdir("cache/dailyplan"):
		print "The directory 'cache/dailyplan' has to exist in work directory"
		sys.exit(1)
	if not os.path.isdir("cache/logs"):
		print "The directory 'cache/logs' has to exist in work directory"
		sys.exit(1)
	"""
	# Not needed yet
	if not os.path.isdir("cache/screenshots"):
		print "The directory 'cache/screenshots' has to exist in work directory"
		sys.exit(1)
	if not os.path.isdir("cache/overlays"):
		print "The directory 'cache/screenhots' has to exist in work directory"
		sys.exit(1)
	"""


def logging_excepthook(type, value, tb):
	"Exception handler that logs"
	logging.debug("Unhandled exception", exc_info=(type, value, tb))
	# continue processing the exception
	sys.__excepthook__(type, value, tb)

def setup_logging():
	logging.basicConfig(level=logging.DEBUG,format="%(asctime)s %(levelname)s:%(name)s %(filename)s:%(lineno)d %(message)s")
	logger = logging.getLogger()
	#ch = logging.StreamHandler()
	#ch.setLevel(logging.DEBUG)	
	handler = handlers.TimedRotatingFileHandler("cache/logs/integrated_playout.log", when="D")
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s %(filename)s:%(lineno)d %(message)s"))
	logger.addHandler(handler)
	sys.excepthook = logging_excepthook

if __name__=="__main__":
	sanity_test()
	setup_logging()
	logging.info("FK Integrated Playout started")
	logging.info("Configuration details: \n"+ configuration.config_strings())

	# Create today's schedule
	schedule = playlist.Schedule()
	schedule.update_from_pg_cache(days=14)
	# Start the player
	playout_service = playout.PlayoutService()
	playout = playout.Playout(
		service=playout_service, 
		#Player=playout.DummyPlayer # Add configuration option for this
		)

	# Start Web
	playoutweb.start_web(None, playout_service, playout, schedule=schedule)

	# Setting the schedule starts playback
	playout.set_schedule(schedule)

	# Heat up the reactor
	from twisted.internet import reactor
	reactor.run()
