import os
import sys
import pip
import urllib2
import mimetypes
import tempfile
try:
    from hashlib import md5
except ImportError:
    import md5 as md5_module
    md5 = md5_module.new

complete_log = []
level = 1
level = pip.Logger.level_for_integer(4-level)
logger = pip.Logger([(level, sys.stdout), (pip.Logger.DEBUG, complete_log.append)])
pip.logger = logger

finder = pip.PackageFinder(find_links=[], index_urls=[pip.pypi_url])

scripts_dir = os.path.dirname(__file__)
download_dir = os.path.join(scripts_dir, '..', 'download')
filename = os.path.join(scripts_dir, '..', 'requirements', 'external_apps.txt')

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

req_set = pip.RequirementSet(build_dir=download_dir, src_dir=download_dir)
unmet_requirements= []

for req in pip.parse_requirements(filename, finder=finder):
    req_set.add_requirement(req)

for req in list(req_set.unnamed_requirements) + req_set.requirements.values():
    try:
        if req.name:
            logger.notify('Searching for: %s' % req.name)
        if req.editable:
            unmet_requirements.append(req)
        else:
            location = req.build_location(download_dir)
            if req.url is None:
                link = finder.find_requirement(req, upgrade=False)
            else:
                link = pip.Link(req.url)
            if link:
                try:
                    md5_hash = link.md5_hash
                    target_url = link.url.split('#', 1)[0]
                    target_file = None
                    try:
                        resp = urllib2.urlopen(target_url)
                    except urllib2.HTTPError, e:
                        logger.fatal("HTTP error %s while getting %s" % (e.code, link))
                        raise
                    except IOError, e:
                        # Typically an FTP error
                        logger.fatal("Error %s while getting %s" % (e, link))
                        raise
                    content_type = resp.info()['content-type']
                    if content_type.startswith('text/html'):
                        unmet_requirements.append(req)
                        continue
                    filename = link.filename
                    ext = pip.splitext(filename)
                    if not ext:
                        ext = mimetypes.guess_extension(content_type)
                        filename += ext
                    temp_location = os.path.join(download_dir, filename)
                    if os.path.exists(temp_location):
                        logger.notify('Skipping %s. File exists.' % filename)
                        continue
                    fp = open(temp_location, 'wb')
                    if md5_hash:
                        download_hash = md5()
                    try:
                        total_length = int(resp.info()['content-length'])
                    except (ValueError, KeyError):
                        total_length = 0
                    downloaded = 0
                    show_progress = total_length > 40*1000 or not total_length
                    show_url = link.show_url
                    try:
                        if show_progress:
                            if total_length:
                                logger.start_progress('Downloading %s (%s): ' % (show_url, pip.format_size(total_length)))
                            else:
                                logger.start_progress('Downloading %s (unknown size): ' % show_url)
                        else:
                            logger.notify('Downloading %s' % show_url)
                        logger.debug('Downloading from URL %s' % link)
                        while 1:
                            chunk = resp.read(4096)
                            if not chunk:
                                break
                            downloaded += len(chunk)
                            if show_progress:
                                if not total_length:
                                    logger.show_progress('%s' % pip.format_size(downloaded))
                                else:
                                    logger.show_progress('%3i%%  %s' % (100*downloaded/total_length, pip.format_size(downloaded)))
                            if md5_hash:
                                download_hash.update(chunk)
                            fp.write(chunk)
                        fp.close()
                    finally:
                        if show_progress:
                            logger.end_progress('%s downloaded' % pip.format_size(downloaded))
                    if md5_hash:
                        download_hash = download_hash.hexdigest()
                        if download_hash != md5_hash:
                            logger.fatal("MD5 hash of the package %s (%s) doesn't match the expected hash %s!"
                                         % (link, download_hash, md5_hash))
                            raise pip.InstallationError('Bad MD5 hash for package %s' % link)
                except urllib2.HTTPError, e:
                    logger.fatal('Could not install requirement %s because of error %s'
                                 % (req, e))
                    raise InstallationError(
                        'Could not install requirement %s because of HTTP error %s for URL %s'
                        % (req, e, url))
    except pip.DistributionNotFound:
        logger.debug('Downloading %s was not successful. Package released?' % req)

logger.notify('The following requirements were not downloaded and should be packaged manually:')
for req in unmet_requirements:
    logger.notify("%s" % req)
