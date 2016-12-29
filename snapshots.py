import boto3


class Snapshot:
    def __init__(self, id, name, volumeId, time):
        self.id = id
        self.name = name
        self.volumeId = volumeId
        self.time = time
        self.parseName()

    def parseName(self):
        split = self.name.split(' ', 20)
        self.ami = ''
        for i in split:
            if i.find('ami-') > -1:
                self.ami = i


class Image:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Volume:
    def __init__(self, id, name):
        self.id = id
        self.name = name


print('Starting...')
ec2Client = boto3.client('ec2')
snapshots = []
images = []
volumes = []

print('Collecting Snapshots')
for s in ec2Client.describe_snapshots(OwnerIds=['self'])['Snapshots']:
    snap = Snapshot(s['SnapshotId'], s['Description'], s['VolumeId'], s['StartTime'])
    snap.parseName()
    snapshots.append(snap)

print('Collecting Images')
for i in ec2Client.describe_images(Owners=['self'])['Images']:
    images.append(Image(i['ImageId'], i['Name']))

print('Collecting Volumes')
for v in ec2Client.describe_volumes()['Volumes']:
    volumes.append(Volume(v['VolumeId'], ''))

print('Found %d snapshots' % len(snapshots))
print('Found %d images' % len(images))
print('Found %d volumes' % len(volumes))

notused = []
for s in snapshots:
    used = False
    for i in images:
        if (i.id == s.ami):
            used = True

    for v in volumes:
        if (v.id == s.volumeId):
            used = True

    if not used:
        notused.append(s)

print('Found %d unused Snaphosts' % len(notused))

response = raw_input('Do you want to delete them all? [y,N]')

if (response == 'y' or response == 'Y'):
    print('Starting deletion')

    counter = 0
    for s in notused:
        ec2Client.delete_snapshot(SnapshotId=s.id)
        counter += 1

    print('Deleted %d Snapshots' % counter)
