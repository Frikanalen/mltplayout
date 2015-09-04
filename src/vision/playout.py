import glob
import datetime
import os
import logging
import zope.interface
from twisted.internet import reactor
from twistedschedule.interfaces import ISchedule 
from twistedschedule.task import ScheduledCall
import playlist
import vlc
import clock
import jukebox
from configuration import configuration

# TODO: Ident, loop, etc should be full program obects and not be hardcoded in playout.py
IDENT_LENGTH = 27.0
IDENT_FILENAME = os.path.join(configuration.ident_media_root, "FrikanalenVignett.avi")
LOOP_FILENAME = os.path.join(configuration.ident_media_root, "FrikanalenLoop.avi")

class VLCPlayer(object):
    def __init__(self):
        self.inst = vlc.Instance(
            '--aout=alsa --sub-filter=logo --no-video-title-show --snapshot-format=jpg ' \
            #'--monitor-par=1:1 --aspect-ratio=5:4 ' \
            #' --vout=opengl ' + \
            ' --no-osd --no-snapshot-preview ' \
            #' -vvv ' \
            #" --sout #transcode{vcodec=mp4v,acodec=mpga,vb=400,ab=128}:standard{access=http,mux=ogg,dst=localhost:8011}"
            ) #--sub-filter=marq
        self.player = self.inst.media_player_new()
        #self.player.set_fullscreen(True) # Must not be true for Groth
        self.player.video_set_deinterlace("disabled\0")
        self.mlp = self.inst.media_list_player_new()
        self.mlp.set_media_player(self.player)
        self.loop = self.inst.media_new(LOOP_FILENAME)
        self.overlay_call = None
        self.state = None
        # TODO: Fix vlc-events. Doesn't work under Linux. Not threadsafe? ABI-mismatch?
        #self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self._addNewPlaceholder)
        #self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEncounteredError, self._error)

        self.pause_screen()
        reactor.callLater(1.0, self._force_aspectratio, None)
    
    def _error(self, foo):
        logging.critical("libvlc event: MediaPlayerEncounteredError - Playback probably stopped and screen black.")
    
    def _addNewPlaceholder(self, foo):
        logging.debug("libvlc event: Playback started.")
        self.ml.add_media(self.placeholder)
     
    def _force_aspectratio(self, foo):
        self.player.video_set_aspect_ratio("5:4")
        reactor.callLater(1.0, self._force_aspectratio, None)

    def _swap_overlay(self):
        # Rotate overlays
        """
        overlays = ["stills/sendeplan-a.png", "stills/sendeplan-b.png"]
        fn = overlays[self.overlay_n % len(overlays)]
        self.overlay_n += 1
        self.player.video_set_logo_string(vlc.VideoLogoOption.file, fn)
        self.player.video_set_logo_int(vlc.VideoLogoOption.delay, 0)
        self.overlay_call = reactor.callLater(4.0, self._swap_overlay)
        """
        pass

    def play_program(self, program=None, resume_offset=0):
        self.still = None
        ml = self.inst.media_list_new()
        if program is not None:
            self.player.video_set_logo_int(vlc.VideoLogoOption.delay, 0)
            self.player.video_set_logo_string(vlc.VideoLogoOption.file, "stills/screenbug.png")
            self.state = "video"
            # TODO: Fallback if the folder is empty
            media_path = program.get_filename()
            if os.path.exists(media_path):
                media = self.inst.media_new(media_path)
                ml.add_media(media)
                # Kill overlays
                if self.overlay_call:
                    self.overlay_call.cancel()
                    self.overlay_call = None
            else:
                logging.error("Didn't find file. Playback never started: %s" % media_path)
        else:
            # Reset & show overlays
            self._swap_overlay()
            self.state = "pase"

        # Add background for pauses
        for n in range(6000):
        #for n in range(2):
            ml.add_media(self.loop)
        self.ml = ml

        self.mlp.set_media_player(self.player)
        self.mlp.pause() # This causes a bit less flashing when changing media
        self.mlp.set_media_list(ml)
        self.mlp.play_item_at_index(0)
        # Handle playback and resume offset
        offset = resume_offset
        if program and program.playback_offset:
            offset += program.playback_offset
        if offset:
            self.player.set_time(int(offset*1000))

    def show_still(self, filename):
        picture = self.inst.media_new(filename)
        ml = self.inst.media_list_new()
        ml.add_media(picture)
        self.mlp.pause() # This causes a bit less flashing when changing media
        self.mlp.set_media_list(ml)
        self.mlp.play_item_at_index(0)
        self.state = "still"

    def pause_screen(self):
        self.overlay_n = 0
        self.play_program()

    def seconds_until_end_of_playing_video(self):
        return (self.player.get_length()-self.player.get_time()) / 1000.

    def snapshot(self):
        # TODO: Change all instances of cache/ to os.path.join(configuration....)
        filename = "cache/snapshots"
        res = self.player.video_take_snapshot(0, filename, 0, 0) # input, filename, width, height
        if res == 0:
            logging.info("Screenshot taken")
        else:
            logging.warning("Screenshot failed")

# Create a new dummy player!
import mlt

class MLTPlayer(object):
    def __init__(self):
        mlt.Factory().init( )
        self.profile = mlt.Profile( )
        self.mlt_consumer = mlt.Consumer( self.profile, "sdl" )
        #self.mlt_consumer = mlt.Consumer( self.profile, "decklink" )
	#self.mlt_consumer.set("fullscreen", 1)
        self.loop = mlt.Producer( self.profile, LOOP_FILENAME)
        #self.loop.set("force_aspect_ratio", 1.0)
        self.loop.set("eof", "loop")
        #self.playing_consumer = None
        self.mlt_consumer.set( "rescale", "none" )
        #self.overlay_call = None
        self.state = None
        self.pause_screen()
        #self.mlt_consumer.listen("producer-changed", None, self.blah )
        self.mlt_consumer.start( )
        print "MLT profile desc", self.profile.description()
        print "Framerate", self.profile.frame_rate_num()
        print "Width/Height/Progressive", self.profile.width(), self.profile.height(), self.profile.progressive()
    
    def blah(self):
        print "xyz"

    def _error(self, foo):
        logging.critical("libvlc event: MediaPlayerEncounteredError - Playback probably stopped and screen black.")
    
    def _mlt_watermark(self, producer):
        filt = mlt.Filter(self.profile, 'watermark:/home/phed/Playout/stills/screenbug.png') 
        filt.connect(producer)
        return filt

    def play_program(self, program=None, resume_offset=0):
        self.still = None
        if program is not None:
            #self.player.video_set_logo_int(vlc.VideoLogoOption.delay, 0)
            #self.player.video_set_logo_string(vlc.VideoLogoOption.file, "stills/screenbug.png")
            self.state = "video"
            # TODO: Fallback if the folder is empty
            media_path = program.get_filename()
            if os.path.exists(media_path):
                producer = mlt.Producer( self.profile, media_path )
                producer.set("force_aspect_ratio", 1.0)
		#producer.set("video_delay", "2.5")
                if program.loop:
                    producer.set("eof", "loop")
	        watermarked = self._mlt_watermark(producer)
                self.mlt_consumer.connect(watermarked)
                #self.playing_producer = producer
                # Kill overlays
                #if self.overlay_call:
                #    self.overlay_call.cancel()
                #    self.overlay_call = None
            else:
                logging.error("Didn't find file. Playback never started: %s" % media_path)
        else:
            # Reset & show overlays
            #self._swap_overlay()
            #if not self.playing_consumer:
            watermarked = self._mlt_watermark(self.loop)
            self.mlt_consumer.connect(watermarked)
        # Handle playback and resume offset
        offset = resume_offset
        if program and program.playback_offset:
            offset += program.playback_offset
        if offset:
            producer.seek(int(offset*25))

    def show_still(self, filename):
        producer = mlt.Producer( self.profile, filename )
        self.mlt_consumer.connect( producer )
        self.state = "still"

    def pause_screen(self):
        self.overlay_n = 0
        self.play_program()

    def seconds_until_end_of_playing_video(self):
        return (self.player.get_length()-self.player.get_time()) / 1000.

    def snapshot(self):
        # TODO: Change all instances of cache/ to os.path.join(configuration....)
        filename = "cache/snapshots"
        pass

class Playout(object):
    zope.interface.implements(ISchedule)

    def __init__(self, service, Player=MLTPlayer):
        # A provider of random videos
        self.random_provider = jukebox.RandomProvider()
        # Schedule 
        self.schedule = None         
        # Next program to play
        self.next_program = None              
        # Current playing program
        self.playing_program = None
        self.player = Player()
        # A reference to the timed callback which aborts programs
        self.duration_call = None    
        self.delayed_start_call = None
        self.service = service
        self.service.playout = self
        # Still filename, if being displayed
        self.still = None
        # Temporary stack for sequence of videos before going to on_idle
        self.on_end_call_stack=[]

    def set_schedule(self, schedule):
        "Set schedule and start playing"
        self.schedule = schedule
        self.scheduler_task = ScheduledCall(self.cue_next_program)
        self.scheduler_task.start(self)
        self.service.on_set_schedule(schedule)
        if not self.playing_program:
            self.resume_playback()

    def resume_current_program(self):
        current_program = self.playing_program
        if current_program:
            self.cue_program(current_program, current_program.seconds_since_playback())

    def resume_playback(self):
        # TODO: Rename to resume_schedule
        current_program = self.schedule.get_current_program()
        if current_program:
            self.cue_program(current_program, current_program.seconds_since_playback())
        else:
            self.on_idle()

    def cue_next_program(self):
        """Starts the next program

        Set the next program with Playout.set_next_program"""
        if self.next_program:
            self.cue_program(self.next_program)
            self.next_program = None

    def _cancel_pending_calls(self):
        """Stops any pending calls from starting in the future (and disrupt playback)

        This is used whenever a program is started and new calls will be registered
        """
        if self.duration_call and not self.duration_call.called:
            self.duration_call.cancel()
            self.duration_call = None
        if self.delayed_start_call and not self.delayed_start_call.called:
            self.delayed_start_call.cancel()
            self.delayed_start_call = None

    def cue_program(self, program, resume_offset=0):
        """Starts the given program"""
        self._cancel_pending_calls()
        duration_text = "Unknown"
        if program.playback_duration == float("inf"):
            duration_text = "Infinite"            
        elif program.playback_duration:
            duration_text = "%i:%02i" % (program.playback_duration / 60, program.playback_duration % 60)
            # Schedule next call
            delta = program.playback_duration-resume_offset
            if delta <= 0.0:
                self.player.pause_screen()
            else:
                self.duration_call = reactor.callLater(delta, self.on_program_ended)
        logging.info("Playback video_id=%i, offset=%s+%ss name='%s' duration=%s" % (
            program.media_id, 
            str(program.playback_offset), str(resume_offset), program.title, duration_text))
        # Start playback
        self.player.play_program(program, resume_offset=resume_offset)
        self.service.on_playback_started(program)
        self.playing_program = program

    def set_next_program(self, program):
        self.next_program = program
        self.service.on_set_next_program(program)
        if program:
            logging.info("Next scheduled video_id=%i @ %s" % (program.media_id, program.program_start))
        else:
            logging.warning("Scheduled nothing")

    # ISchedule.getDelayForNext
    def getDelayForNext(self):
        # Queue next
        program = self.schedule.get_next_program()
        if program == None:
            self.scheduler_task.stop()
            self.set_next_program(None)
            # This will actually call cue_next_program once more.
            logging.warning("Program schedule empty")
            return 0.0
        self.set_next_program(program)
        return program.seconds_until_playback()

    def stop_schedule(self):
        if self.scheduler_task and self.scheduler_task.running:
            self.scheduler_task.stop()
        #self.set_next_program(None)

    def start_schedule(self):
        self.stop_schedule()
        self.scheduler_task = ScheduledCall(self.cue_next_program)
        self.scheduler_task.start(self)

    def show_still(self, filename="stills/tekniskeprover.png"):
        self._cancel_pending_calls()
        self.stop_schedule()
        self.player.show_still(filename)
        self.service.on_still(filename)
        logging.info("Show still: %s", filename)

    def cancel_still(self):
        logging.info("Cancel still")
        self.service.on_still("")
        self.start_schedule()
        # TODO: resume_current_program?
        self.resume_playback()

    def on_program_ended(self):
        """
        try:
            logging.debug("Video '%s' #%i ended with %.1fs left. " % (
                self.playing_program.title, self.playing_program.media_id, 
                self.player.seconds_until_end_of_playing_video())
                )
            pass
        # TODO: Add proper exception/exceptionlogging
        except:
            logging.warning("Excepted while trying to log on_program_ended")
        """
        if self.on_end_call_stack:
            func = self.on_end_call_stack.pop(0)
            func()
        else:
            self.on_idle()

    def play_jukebox(self):
        logging.info("Jukebox playback start")
        program = self.schedule.new_program()
        limit = 90*60 # 90 minutes long programs max
        if self.next_program:
            limit = min(limit, self.next_program.seconds_until_playback())
        video = self.random_provider.get_random_video(limit)
        program.set_program(
            media_id=video["media_id"], 
            program_start=clock.now(),
            playback_duration=video["duration"],
            title=video["name"])
        self.cue_program(program)

    def play_ident(self):
        logging.info("Ident playback start")
        program = self.schedule.new_program()
        program.set_program(
            media_id=-1, 
            program_start=clock.now(),
            playback_duration=IDENT_LENGTH,
            title="Frikanalen Vignett",
            filename=IDENT_FILENAME)
        self.cue_program(program)

    def on_idle(self):
        time_until_next = float("inf")
        if self.next_program:
            time_until_next = self.next_program.seconds_until_playback()
        # The rules. 
        use_jukebox = configuration.jukebox 
        use_jukebox &= time_until_next > (120+IDENT_LENGTH)
        use_jukebox &= self.random_provider.enough_room(time_until_next)
        if use_jukebox:
            loop_length = 12.0
            PAUSE_LENGTH = IDENT_LENGTH+loop_length
            logging.info("Pause before jukebox: %.1fs" % PAUSE_LENGTH)
            program = self.schedule.new_program()
            program.set_program(-1, 
                program_start=clock.now(), 
                playback_duration=loop_length, 
                title="Jukebox pause screen", 
                filename=LOOP_FILENAME, 
                loop=True)
            self.cue_program(program)
            self.on_end_call_stack.append(self.play_ident)
            self.on_end_call_stack.append(self.play_jukebox)
        elif time_until_next >= 12+IDENT_LENGTH:
            logging.info("Pause idle: %.1fs" % time_until_next)
            PAUSE_LENGTH = time_until_next
            program = self.schedule.new_program()
            program.set_program(-1, 
                program_start=clock.now(), 
                playback_duration=time_until_next-IDENT_LENGTH, 
                title="Pause screen", 
                filename=LOOP_FILENAME,
                loop=True)
            self.cue_program(program)
            self.on_end_call_stack.append(self.play_ident)
        else:
            logging.info("Short idle: %.1fs" % time_until_next)
            # Show pausescreen
            program = self.schedule.new_program()
            t = None
            if self.next_program:
                t = self.next_program.seconds_until_playback()
            program.set_program(-1, program_start=clock.now(), playback_duration=t, title="Pause screen", filename=LOOP_FILENAME, loop=True)
            #self.cue_program(program) # TODO: Doesn't handle looping
            self.player.pause_screen()
            self.playing_program = program
            self.service.on_playback_started(program)

import weakref
class PlayoutService(object):
    def __init__(self):
        self.observers = weakref.WeakKeyDictionary()

    def add_observer(self, observer):
        self.observers[observer] = True
        observer.on_playback_started(self.playout.playing_program)
        observer.on_set_next_program(self.playout.next_program)
        if self.playout.still:
            observer.on_still(self.playout.still)

    def remove_observer(self, observer):
        del self.observers[observer]

    def on_playback_started(self, program):
        for each in self.observers.keys():
            each.on_playback_started(program)

    def on_still(self, name):
        for each in self.observers.keys():
            each.on_still(name)        

    def on_set_schedule(self, program):
        for each in self.observers.keys():
            each.on_set_schedule(program)

    def on_set_next_program(self, program):
        for each in self.observers.keys():
            each.on_set_next_program(program)

def start_test_player():
    logging.basicConfig(level=logging.DEBUG,format="%(asctime)s %(levelname)s:%(name)s %(filename)s:%(lineno)d %(message)s")
    import playoutweb 
    service = PlayoutService()

    schedule = playlist.Schedule()
    v = schedule.new_program()
    v.set_program(1758, clock.now() - datetime.timedelta(0, 5), title="First", 
        playback_offset=10, playback_duration=10.0)
    schedule.add(v)
    for n in range(1):
        delta = datetime.timedelta(0, 6+(n)*10.0) 
        v = schedule.new_program()
        v.set_program(1758, clock.now() + delta, title="No %i" % n, 
            playback_offset=30+60*n, playback_duration=9.0)
        print "Added %i @ %s" % (n, v.program_start)
        schedule.add(v)
    player = Playout(service)
    player.set_schedule(schedule)
    #playoutweb.start_web(None, playout_service=service, playout=player, schedule=schedule, port=8888)
    def test():
        print "hoi"
    reactor.callLater(4.0, player.show_still)
    reactor.callLater(7.0, player.cancel_still)
    return player

if __name__=="__main__":
    start_test_player()
    reactor.run()
