import basc_py4chan
from time import sleep

'''
        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
'''


class ThreadMonitor:
    # TODO: Abstract this thread to any general
    def __init__(self, target_board, thread_keywords, post_save_path):
        """
        ThreadMonitor
        self.vg: 4chan board /vg/
        self.thrd: /rlg/ thread
        self.last_post: post id for the last post printed to the display
        self.last_post_saved: post id saved to a text file to allow uninterrupted shutdown and startup
        """
        self.target_board = basc_py4chan.Board(target_board)
        self.thrd = None
        self.thrd_kywrd = thread_keywords
        self.post_save = post_save_path
        with open(self.post_save, 'r') as f:
            self.last_post = int(f.read().rstrip())
            f.close()
        self.last_post_saved = self.last_post
        self.thread_finder()

    def thread_finder(self):
        """
        Updates the thrd attribute to the current thread.
        :return: None
        """
        threads = self.target_board.get_all_threads(expand=False)
        candidate_threads = []
        for t in threads:
            for key in self.thrd_kywrd:
                if key in t.semantic_slug:
                    candidate_threads.append(t)

        if len(candidate_threads) == 0:
            self.thrd = None
            # No thread found, sleep 15 seconds before checking again
            sleep(15)
        elif len(candidate_threads) == 1:
            self.thrd = candidate_threads[0]
        else:
            last_reply_max = 0
            for index in range(len(candidate_threads)):
                if candidate_threads[index].bumplimit is False:
                    if candidate_threads[index].last_reply_id > last_reply_max:
                        last_reply_max = index
            print("index found " + str(last_reply_max))
            self.thrd = candidate_threads[last_reply_max]

    def get_next_reply(self):
        """
        Find a thread and update thrd attribute is closed or missing if missing. Updates the thread, finds the next
        post that has a post id greater than the last_post attribute, and returns the text of that post. Saves the new
        post id if significantly newer.
        :return:
        """
        if self.thrd is None:
            self.thread_finder()
            return None
        else:
            self.thrd.update()
            if self.thrd.archived or self.thrd.closed or self.thrd.is_404:
                self.thrd = None
                return None
            else:
                for post in self.thrd.all_posts:
                    if post.post_id > self.last_post:
                        self.last_post = post.post_id
                        if self.last_post > self.last_post_saved + 3000:
                            f = open(self.post_save, 'w')
                            f.write(str(self.last_post))
                            self.last_post_saved = self.last_post
                        return post.text_comment.replace('\n', ' ')
                # No new post found, sleep 15 seconds before checking again
                sleep(15)
                return None
